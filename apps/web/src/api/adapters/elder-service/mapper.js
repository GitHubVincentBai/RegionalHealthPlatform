import { createMockElder } from "../../../modules/elder/mock.js";

const RISK_LEVEL_LABELS = {
  critical: "高风险",
  high: "高风险",
  medium: "中风险",
  low: "低风险",
  高风险: "高风险",
  中风险: "中风险",
  低风险: "低风险",
};

const RISK_LEVEL_TO_API = {
  高风险: "high",
  中风险: "medium",
  低风险: "low",
};

const CHECK_IN_STATUS_LABELS = {
  checked_in: "已入住",
  pre_admission: "待入住",
  discharged: "已离院",
  已入住: "已入住",
  待入住: "待入住",
  已离院: "已离院",
};

const CHECK_IN_STATUS_TO_API = {
  已入住: "checked_in",
  待入住: "pre_admission",
  已离院: "discharged",
};

function trimText(value, fallback = "") {
  return typeof value === "string" ? value.trim() || fallback : fallback;
}

export function mapRiskLevelLabel(value, isHighRisk = false) {
  if (isHighRisk && !value) {
    return "高风险";
  }

  return RISK_LEVEL_LABELS[String(value || "").toLowerCase()] || trimText(value, "中风险");
}

export function mapCheckInStatusLabel(value) {
  return CHECK_IN_STATUS_LABELS[String(value || "").toLowerCase()] || trimText(value, "待入住");
}

export function mapRiskLevelToApi(value) {
  return RISK_LEVEL_TO_API[trimText(value, "中风险")] || String(value || "medium").toLowerCase();
}

export function mapCheckInStatusToApi(value) {
  return CHECK_IN_STATUS_TO_API[trimText(value, "待入住")] || String(value || "pre_admission").toLowerCase();
}

export function createGeneratedElderId() {
  return `E-${Date.now()}`;
}

export function mapElderProfileToViewModel(profile) {
  const familyContacts = Array.isArray(profile.family_contacts) ? profile.family_contacts : [];
  const primaryContact = familyContacts.find((contact) => contact.is_primary_contact) || familyContacts[0] || null;
  const stayInfo = profile.stay_info || {};
  const currentStayStatus = trimText(profile.current_stay_status || stayInfo.check_in_status, "pre_admission");
  const stationId = trimText(profile.station_id, "");

  return {
    elderId: trimText(profile.elder_id, "待生成"),
    elderCode: trimText(profile.elder_code, "待生成"),
    fullName: trimText(profile.full_name, "未命名长者"),
    gender: trimText(profile.gender, "待补充"),
    age: Number(profile.age || 0),
    birthDate: trimText(profile.birth_date, "待补充"),
    phone: trimText(profile.phone, "待补充"),
    idCard: trimText(profile.id_card, "待补充"),
    riskLevel: mapRiskLevelLabel(profile.risk_level, Boolean(profile.is_high_risk)),
    status: mapCheckInStatusLabel(currentStayStatus),
    profileStatus: trimText(profile.status, "active"),
    currentStayStatus,
    station: stationId || "待补充",
    stationId,
    room: trimText(stayInfo.room_id, "待安排"),
    bed: trimText(stayInfo.bed_id, "待安排"),
    family: trimText(primaryContact?.family_name, "待补充"),
    familyRelation: trimText(primaryContact?.relation_type, "待补充"),
    familyPhone: trimText(primaryContact?.phone, "待补充"),
    familyContacts,
    checkInDate: trimText(stayInfo.check_in_date, "待安排"),
    note: trimText(stayInfo.notes, "暂无备注"),
    source: "api",
  };
}

export function calculateArchiveSummary(elders, total = elders.length) {
  return {
    total,
    checkedIn: elders.filter((elder) => elder.status === "已入住").length,
    waitingCheckIn: elders.filter((elder) => elder.status === "待入住").length,
    highRisk: elders.filter((elder) => elder.riskLevel === "高风险").length,
  };
}

export function mapListResponseToArchive(response) {
  const elders = Array.isArray(response.items) ? response.items.map(mapElderProfileToViewModel) : [];

  return {
    elders,
    summary: calculateArchiveSummary(elders, Number(response.total || elders.length)),
    pagination: {
      total: Number(response.total || elders.length),
      page: Number(response.page || 1),
      pageSize: Number(response.page_size || elders.length || 20),
    },
  };
}

export function buildCreatePayload(draft) {
  const elderId = trimText(draft.elderId) || createGeneratedElderId();
  const familyName = trimText(draft.familyName);
  const familyPhone = trimText(draft.familyPhone);
  const stationId = trimText(draft.stationId || draft.station, "station-longhu");

  return {
    elder_id: elderId,
    elder_code: trimText(draft.elderCode) || null,
    full_name: trimText(draft.fullName, "未命名长者"),
    gender: trimText(draft.gender, "unknown"),
    age: Number(draft.age || 0),
    birth_date: trimText(draft.birthDate),
    phone: trimText(draft.phone),
    id_card: trimText(draft.idCard),
    risk_level: mapRiskLevelToApi(draft.riskLevel),
    status: "active",
    station_id: stationId,
    stay_info: {
      check_in_status: mapCheckInStatusToApi(draft.checkInStatus),
      room_id: trimText(draft.room),
      bed_id: trimText(draft.bed),
      check_in_date: trimText(draft.checkInDate),
      notes: trimText(draft.note),
    },
    family_contacts:
      familyName && familyPhone
        ? [
            {
              family_name: familyName,
              relation_type: trimText(draft.familyRelation, "家属"),
              phone: familyPhone,
              is_primary_contact: true,
            },
          ]
        : [],
  };
}

export function createMockElderFromDraft(draft, elderId) {
  return createMockElder({
    elderId,
    elderCode: trimText(draft.elderCode, `HPT-EL-${String(Date.now()).slice(-4)}`),
    fullName: trimText(draft.fullName, "未命名长者"),
    gender: trimText(draft.gender, "待补充"),
    age: Number(draft.age || 0),
    birthDate: trimText(draft.birthDate, "待补充"),
    phone: trimText(draft.phone, "待补充"),
    idCard: trimText(draft.idCard, "待补充"),
    riskLevel: mapRiskLevelLabel(draft.riskLevel),
    status: mapCheckInStatusLabel(draft.checkInStatus),
    currentStayStatus: mapCheckInStatusToApi(draft.checkInStatus),
    station: trimText(draft.station, "待补充"),
    stationId: trimText(draft.stationId || draft.station, "待补充"),
    room: trimText(draft.room, "待安排"),
    bed: trimText(draft.bed, "待安排"),
    family: trimText(draft.familyName, "待补充"),
    familyRelation: trimText(draft.familyRelation, "待补充"),
    familyPhone: trimText(draft.familyPhone, "待补充"),
    familyContacts:
      trimText(draft.familyName) && trimText(draft.familyPhone)
        ? [
            {
              family_name: trimText(draft.familyName),
              relation_type: trimText(draft.familyRelation, "家属"),
              phone: trimText(draft.familyPhone),
              is_primary_contact: true,
            },
          ]
        : [],
    checkInDate: trimText(draft.checkInDate, "待安排"),
    note: trimText(draft.note, "已保存 mock 入住草稿。"),
    source: "mock",
  });
}
