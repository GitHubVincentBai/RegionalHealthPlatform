from __future__ import annotations

import os
from collections.abc import Mapping
from threading import Lock

from elder_service.application.repository import ElderProfileRepository
from elder_service.domain.models import ElderProfile, FamilyContact, StayInfo


DEFAULT_POSTGRES_ENV = {
    "ELDER_SERVICE_DB_HOST": "127.0.0.1",
    "ELDER_SERVICE_DB_PORT": "5432",
    "ELDER_SERVICE_DB_NAME": "elder_service",
    "ELDER_SERVICE_DB_USER": "postgres",
    "ELDER_SERVICE_DB_PASSWORD": "postgres",
    "ELDER_SERVICE_DB_SSLMODE": "disable",
}


def build_postgres_dsn_from_env(env: Mapping[str, str] | None = None) -> str:
    env = env or os.environ
    direct_dsn = env.get("ELDER_SERVICE_DB_DSN") or env.get("DATABASE_URL")
    if direct_dsn:
        return direct_dsn

    values = {key: env.get(key, default) for key, default in DEFAULT_POSTGRES_ENV.items()}
    return (
        "postgresql://{user}:{password}@{host}:{port}/{name}"
        "?sslmode={sslmode}"
    ).format(
        user=values["ELDER_SERVICE_DB_USER"],
        password=values["ELDER_SERVICE_DB_PASSWORD"],
        host=values["ELDER_SERVICE_DB_HOST"],
        port=values["ELDER_SERVICE_DB_PORT"],
        name=values["ELDER_SERVICE_DB_NAME"],
        sslmode=values["ELDER_SERVICE_DB_SSLMODE"],
    )


class PostgresElderProfileRepository(ElderProfileRepository):
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._initialized = False
        self._initialize_lock = Lock()

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "PostgresElderProfileRepository":
        return cls(build_postgres_dsn_from_env(env))

    def save(self, profile: ElderProfile) -> ElderProfile:
        psycopg, dict_row = _load_psycopg()
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            self._initialize(connection)
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO elder_profiles (
                        elder_id,
                        elder_code,
                        full_name,
                        gender,
                        age,
                        birth_date,
                        phone,
                        id_card,
                        risk_level,
                        status,
                        station_id,
                        admission_id,
                        check_in_status,
                        room_id,
                        bed_id,
                        check_in_date,
                        notes
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (elder_id) DO UPDATE SET
                        elder_code = EXCLUDED.elder_code,
                        full_name = EXCLUDED.full_name,
                        gender = EXCLUDED.gender,
                        age = EXCLUDED.age,
                        birth_date = EXCLUDED.birth_date,
                        phone = EXCLUDED.phone,
                        id_card = EXCLUDED.id_card,
                        risk_level = EXCLUDED.risk_level,
                        status = EXCLUDED.status,
                        station_id = EXCLUDED.station_id,
                        admission_id = EXCLUDED.admission_id,
                        check_in_status = EXCLUDED.check_in_status,
                        room_id = EXCLUDED.room_id,
                        bed_id = EXCLUDED.bed_id,
                        check_in_date = EXCLUDED.check_in_date,
                        notes = EXCLUDED.notes
                    """,
                    (
                        profile.elder_id,
                        profile.elder_code,
                        profile.full_name,
                        profile.gender,
                        profile.age,
                        profile.birth_date,
                        profile.phone,
                        profile.id_card,
                        profile.risk_level,
                        profile.status,
                        profile.station_id,
                        profile.stay_info.admission_id,
                        profile.stay_info.check_in_status,
                        profile.stay_info.room_id,
                        profile.stay_info.bed_id,
                        profile.stay_info.check_in_date,
                        profile.stay_info.notes,
                    ),
                )
                cursor.execute(
                    "DELETE FROM elder_family_contacts WHERE elder_id = %s",
                    (profile.elder_id,),
                )
                if profile.family_contacts:
                    cursor.executemany(
                        """
                        INSERT INTO elder_family_contacts (
                            elder_id,
                            family_name,
                            relation_type,
                            phone,
                            is_primary_contact
                        ) VALUES (%s, %s, %s, %s, %s)
                        """,
                        [
                            (
                                profile.elder_id,
                                contact.family_name,
                                contact.relation_type,
                                contact.phone,
                                contact.is_primary_contact,
                            )
                            for contact in profile.family_contacts
                        ],
                    )
            connection.commit()
        return profile

    def get(self, elder_id: str) -> ElderProfile | None:
        psycopg, dict_row = _load_psycopg()
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            self._initialize(connection)
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        elder_id,
                        elder_code,
                        full_name,
                        gender,
                        age,
                        birth_date,
                        phone,
                        id_card,
                        risk_level,
                        status,
                        station_id,
                        admission_id,
                        check_in_status,
                        room_id,
                        bed_id,
                        check_in_date,
                        notes
                    FROM elder_profiles
                    WHERE elder_id = %s
                    """,
                    (elder_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    return None
                family_contacts = self._fetch_family_contacts(cursor, elder_id)
        return self._row_to_profile(row, family_contacts)

    def list_all(self) -> list[ElderProfile]:
        psycopg, dict_row = _load_psycopg()
        with psycopg.connect(self._dsn, row_factory=dict_row) as connection:
            self._initialize(connection)
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        elder_id,
                        elder_code,
                        full_name,
                        gender,
                        age,
                        birth_date,
                        phone,
                        id_card,
                        risk_level,
                        status,
                        station_id,
                        admission_id,
                        check_in_status,
                        room_id,
                        bed_id,
                        check_in_date,
                        notes
                    FROM elder_profiles
                    ORDER BY elder_id
                    """
                )
                profile_rows = cursor.fetchall()
                cursor.execute(
                    """
                    SELECT elder_id, family_name, relation_type, phone, is_primary_contact
                    FROM elder_family_contacts
                    ORDER BY elder_id, id
                    """
                )
                family_rows = cursor.fetchall()

        family_by_elder: dict[str, list[dict[str, object]]] = {}
        for row in family_rows:
            family_by_elder.setdefault(str(row["elder_id"]), []).append(row)

        return [
            self._row_to_profile(row, family_by_elder.get(str(row["elder_id"]), []))
            for row in profile_rows
        ]

    def _initialize(self, connection: object) -> None:
        if self._initialized:
            return

        with self._initialize_lock:
            if self._initialized:
                return

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS elder_profiles (
                        elder_id TEXT PRIMARY KEY,
                        elder_code TEXT NOT NULL UNIQUE,
                        full_name TEXT NOT NULL,
                        gender TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        birth_date TEXT NOT NULL DEFAULT '',
                        phone TEXT NOT NULL DEFAULT '',
                        id_card TEXT NOT NULL DEFAULT '',
                        risk_level TEXT NOT NULL,
                        status TEXT NOT NULL,
                        station_id TEXT NOT NULL,
                        admission_id TEXT NOT NULL DEFAULT '',
                        check_in_status TEXT NOT NULL,
                        room_id TEXT NOT NULL DEFAULT '',
                        bed_id TEXT NOT NULL DEFAULT '',
                        check_in_date TEXT NOT NULL DEFAULT '',
                        notes TEXT NOT NULL DEFAULT '',
                        CONSTRAINT elder_profiles_check_in_status_chk
                            CHECK (check_in_status IN ('pre_admission', 'checked_in', 'discharged')),
                        CONSTRAINT elder_profiles_bed_requires_room_chk
                            CHECK (bed_id = '' OR room_id <> '')
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS elder_family_contacts (
                        id BIGSERIAL PRIMARY KEY,
                        elder_id TEXT NOT NULL REFERENCES elder_profiles(elder_id) ON DELETE CASCADE,
                        family_name TEXT NOT NULL,
                        relation_type TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        is_primary_contact BOOLEAN NOT NULL DEFAULT FALSE
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS elder_family_contacts_primary_contact_uidx
                    ON elder_family_contacts (elder_id)
                    WHERE is_primary_contact
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS elder_profiles_station_status_idx
                    ON elder_profiles (station_id, status)
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS elder_profiles_risk_level_idx
                    ON elder_profiles (risk_level)
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS elder_profiles_check_in_status_idx
                    ON elder_profiles (check_in_status)
                    """
                )
                cursor.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS elder_profiles_checked_in_bed_uidx
                    ON elder_profiles (bed_id)
                    WHERE bed_id <> '' AND check_in_status = 'checked_in'
                    """
                    )
            connection.commit()
            self._initialized = True

    def _fetch_family_contacts(
        self, cursor: object, elder_id: str
    ) -> list[dict[str, object]]:
        cursor.execute(
            """
            SELECT elder_id, family_name, relation_type, phone, is_primary_contact
            FROM elder_family_contacts
            WHERE elder_id = %s
            ORDER BY id
            """,
            (elder_id,),
        )
        return cursor.fetchall()

    def _row_to_profile(
        self, row: dict[str, object], family_rows: list[dict[str, object]]
    ) -> ElderProfile:
        return ElderProfile(
            elder_id=str(row["elder_id"]),
            elder_code=str(row["elder_code"]),
            full_name=str(row["full_name"]),
            gender=str(row["gender"]),
            age=int(row["age"]),
            birth_date=str(row["birth_date"]),
            phone=str(row["phone"]),
            id_card=str(row["id_card"]),
            risk_level=str(row["risk_level"]),
            status=str(row["status"]),
            station_id=str(row["station_id"]),
            stay_info=StayInfo(
                admission_id=str(row["admission_id"]),
                check_in_status=str(row["check_in_status"]),
                room_id=str(row["room_id"]),
                bed_id=str(row["bed_id"]),
                check_in_date=str(row["check_in_date"]),
                notes=str(row["notes"]),
            ),
            family_contacts=[
                FamilyContact(
                    family_name=str(contact["family_name"]),
                    relation_type=str(contact["relation_type"]),
                    phone=str(contact["phone"]),
                    is_primary_contact=bool(contact["is_primary_contact"]),
                )
                for contact in family_rows
            ],
        )


def _load_psycopg() -> tuple[object, object]:
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "elder-service PostgreSQL repository requires psycopg. "
            "Install the service with `python3 -m pip install -e \".[test]\"` "
            "or use `bash scripts/run_python_elder_checks.sh prepare`."
        ) from exc

    return psycopg, dict_row
