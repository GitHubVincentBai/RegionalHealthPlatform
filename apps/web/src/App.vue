<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import AppHeader from "./components/AppHeader.vue";
import AppNav from "./components/AppNav.vue";
import DashboardPage from "./views/dashboard/DashboardPage.vue";
import ElderArchivePage from "./views/elder/ElderArchivePage.vue";
import ElderDetailPage from "./views/elder/ElderDetailPage.vue";
import ElderIntakePage from "./views/elder/ElderIntakePage.vue";
import { createElderArchiveService } from "./api/adapters/elder-service/index.js";
import { createElderDraft } from "./modules/elder/mock.js";
import { useHashView } from "./composables/useHashView.js";
import { APP_NAV_ITEMS, getViewConfig } from "./navigation/appViews.js";

const { view, navigate } = useHashView("dashboard");
const elderService = createElderArchiveService();
const appState = reactive({
  summary: {
    total: 0,
    checkedIn: 0,
    waitingCheckIn: 0,
    highRisk: 0,
  },
  elders: [],
  dataSource: "api",
  syncWarning: "",
  listError: "",
  listLoading: false,
  detailLoading: false,
  detailError: "",
  submitLoading: false,
  submitError: "",
  submitSuccess: "",
  filters: {
    search: "",
    stationId: "",
    profileStatus: "",
    riskLevel: "",
    checkInStatus: "",
  },
  pagination: {
    total: 0,
    page: 1,
    pageSize: 20,
  },
  validationErrors: {},
});
const activeElderId = ref("");
const currentElder = ref(null);
const intakeDraft = ref(createElderDraft());

const selectedArchiveElder = computed(
  () => appState.elders.find((elder) => elder.elderId === activeElderId.value) ?? appState.elders[0] ?? null,
);
const currentViewConfig = computed(() => getViewConfig(view.value));
const pageTitle = computed(() => currentViewConfig.value.title);
const pageDescription = computed(() => currentViewConfig.value.description);

const mergeSourceState = (result) => {
  appState.dataSource = result.source || "api";
  appState.syncWarning = result.warning || "";
};

const syncArchiveState = (archive) => {
  appState.summary = archive.summary;
  appState.elders = archive.elders;
  appState.pagination = archive.pagination || appState.pagination;
};

const toArchiveQuery = () => ({
  search: appState.filters.search,
  station_id: appState.filters.stationId,
  status: appState.filters.profileStatus,
  risk_level: appState.filters.riskLevel,
  check_in_status: appState.filters.checkInStatus,
  page: appState.pagination.page,
  page_size: appState.pagination.pageSize,
});

const loadArchive = async (preferredElderId = activeElderId.value) => {
  appState.listLoading = true;
  appState.listError = "";

  try {
    const archive = await elderService.loadArchive(toArchiveQuery());
    syncArchiveState(archive);
    mergeSourceState(archive);

    const nextActiveElderId =
      archive.elders.find((elder) => elder.elderId === preferredElderId)?.elderId || archive.elders[0]?.elderId || "";

    activeElderId.value = nextActiveElderId;
  } catch (error) {
    appState.listError = error instanceof Error ? error.message : "长者档案加载失败";
  } finally {
    appState.listLoading = false;
  }
};

const loadElderDetail = async (elderId) => {
  if (!elderId) {
    currentElder.value = null;
    return;
  }

  appState.detailLoading = true;
  appState.detailError = "";

  try {
    const result = await elderService.getElder(elderId);
    currentElder.value = result.elder ?? selectedArchiveElder.value;
    mergeSourceState(result);
  } catch (error) {
    currentElder.value = selectedArchiveElder.value;
    appState.detailError = error instanceof Error ? error.message : "长者详情加载失败";
  } finally {
    appState.detailLoading = false;
  }
};

const selectElder = async (elderId) => {
  activeElderId.value = elderId;
  navigate("elder-detail");
  await loadElderDetail(elderId);
};

const resetIntakeDraft = () => {
  intakeDraft.value = createElderDraft();
  appState.submitError = "";
  appState.submitSuccess = "";
  appState.validationErrors = {};
  navigate("elder-intake");
};

const updateIntakeDraft = (nextDraft) => {
  intakeDraft.value = nextDraft;
  appState.validationErrors = {};
  appState.submitError = "";
  appState.submitSuccess = "";
};

const updateArchiveFilters = (nextFilters) => {
  appState.filters = {
    ...appState.filters,
    ...nextFilters,
  };
};

const applyArchiveFilters = async () => {
  appState.pagination.page = 1;
  await loadArchive();
  await loadElderDetail(activeElderId.value);
};

const resetArchiveFilters = async () => {
  appState.filters = {
    search: "",
    stationId: "",
    profileStatus: "",
    riskLevel: "",
    checkInStatus: "",
  };
  appState.pagination.page = 1;
  await loadArchive();
  await loadElderDetail(activeElderId.value);
};

const validateIntakeDraft = (draft) => {
  const errors = {};

  if (!String(draft.fullName || "").trim()) {
    errors.fullName = "请填写长者姓名";
  }

  if (!String(draft.stationId || draft.station || "").trim()) {
    errors.stationId = "请填写站点编码";
  }

  if (!String(draft.familyName || "").trim()) {
    errors.familyName = "请填写主联系人姓名";
  }

  if (!String(draft.familyPhone || "").trim()) {
    errors.familyPhone = "请填写主联系人电话";
  }

  if (String(draft.bed || "").trim() && !String(draft.room || "").trim()) {
    errors.room = "填写床位前请先填写房间";
  }

  if (draft.checkInStatus === "已入住") {
    if (!String(draft.room || "").trim()) {
      errors.room = "已入住长者必须分配房间";
    }
    if (!String(draft.bed || "").trim()) {
      errors.bed = "已入住长者必须分配床位";
    }
    if (!String(draft.checkInDate || "").trim()) {
      errors.checkInDate = "已入住长者必须填写入住日期";
    }
  }

  return errors;
};

const submitIntakeDraft = async () => {
  const validationErrors = validateIntakeDraft(intakeDraft.value);
  appState.validationErrors = validationErrors;

  if (Object.keys(validationErrors).length > 0) {
    appState.submitError = "请先补全入住办理必填信息";
    return;
  }

  appState.submitLoading = true;
  appState.submitError = "";
  appState.submitSuccess = "";

  try {
    const result = await elderService.createElder(intakeDraft.value);
    mergeSourceState(result);
    appState.filters = {
      search: "",
      stationId: "",
      profileStatus: "",
      riskLevel: "",
      checkInStatus: "",
    };
    await loadArchive(result.elder.elderId);
    await loadElderDetail(result.elder.elderId);
    appState.submitSuccess =
      result.source === "mock"
        ? "已保存 mock 入住草稿，等待 elder-service 恢复后切换真实接口。"
        : "长者档案已同步到 elder-service。";
    intakeDraft.value = createElderDraft();
    navigate("elder-detail");
  } catch (error) {
    appState.submitError = error instanceof Error ? error.message : "长者档案创建失败";
  } finally {
    appState.submitLoading = false;
  }
};

watch(
  view,
  async (nextView) => {
    if (nextView === "elder-list" && !appState.listLoading && appState.elders.length === 0) {
      await loadArchive();
      return;
    }

    if (nextView === "elder-detail" && activeElderId.value && !currentElder.value && !appState.detailLoading) {
      await loadElderDetail(activeElderId.value);
      return;
    }

    if (nextView === "elder-intake" && !intakeDraft.value?.stationId) {
      intakeDraft.value = createElderDraft();
    }
  },
  { immediate: true },
);

onMounted(async () => {
  await loadArchive();
  await loadElderDetail(activeElderId.value);
});
</script>

<template>
  <main class="app-shell">
    <section class="shell-frame">
      <AppHeader :title="pageTitle" :description="pageDescription" />

      <AppNav :current-view="view" :items="APP_NAV_ITEMS" @navigate="navigate" />

      <DashboardPage v-if="view === 'dashboard'" />

      <ElderArchivePage
        v-else-if="view === 'elder-list'"
        :summary="appState.summary"
        :elders="appState.elders"
        :filters="appState.filters"
        :pagination="appState.pagination"
        :selected-elder-id="activeElderId"
        :selected-elder="selectedArchiveElder"
        :loading="appState.listLoading"
        :error-message="appState.listError"
        :data-source="appState.dataSource"
        :sync-warning="appState.syncWarning"
        @select-elder="selectElder"
        @create-draft="resetIntakeDraft"
        @refresh="applyArchiveFilters"
        @apply-filters="applyArchiveFilters"
        @reset-filters="resetArchiveFilters"
        @update:filters="updateArchiveFilters"
      />

      <ElderDetailPage
        v-else-if="view === 'elder-detail'"
        :elder="currentElder"
        :loading="appState.detailLoading"
        :error-message="appState.detailError"
        :data-source="appState.dataSource"
        :sync-warning="appState.syncWarning"
        @back="navigate('elder-list')"
      />

      <ElderIntakePage
        v-else-if="view === 'elder-intake'"
        :draft="intakeDraft"
        :submitting="appState.submitLoading"
        :error-message="appState.submitError"
        :success-message="appState.submitSuccess"
        :data-source="appState.dataSource"
        :sync-warning="appState.syncWarning"
        :validation-errors="appState.validationErrors"
        @back="navigate('elder-list')"
        @update:draft="updateIntakeDraft"
        @submit="submitIntakeDraft"
      />

      <DashboardPage v-else />
    </section>
  </main>
</template>
