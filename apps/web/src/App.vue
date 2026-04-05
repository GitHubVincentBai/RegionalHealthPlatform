<script setup>
import { computed, onMounted, reactive, ref } from "vue";
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
};

const loadArchive = async (preferredElderId = activeElderId.value) => {
  appState.listLoading = true;
  appState.listError = "";

  try {
    const archive = await elderService.loadArchive();
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
  navigate("elder-intake");
};

const updateIntakeDraft = (nextDraft) => {
  intakeDraft.value = nextDraft;
};

const submitIntakeDraft = async () => {
  appState.submitLoading = true;
  appState.submitError = "";

  try {
    const result = await elderService.createElder(intakeDraft.value);
    mergeSourceState(result);
    await loadArchive(result.elder.elderId);
    await loadElderDetail(result.elder.elderId);
    intakeDraft.value = createElderDraft();
    navigate("elder-detail");
  } catch (error) {
    appState.submitError = error instanceof Error ? error.message : "长者档案创建失败";
  } finally {
    appState.submitLoading = false;
  }
};

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
        :selected-elder-id="activeElderId"
        :selected-elder="selectedArchiveElder"
        :loading="appState.listLoading"
        :error-message="appState.listError"
        :data-source="appState.dataSource"
        :sync-warning="appState.syncWarning"
        @select-elder="selectElder"
        @create-draft="resetIntakeDraft"
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
        :data-source="appState.dataSource"
        :sync-warning="appState.syncWarning"
        @back="navigate('elder-list')"
        @update:draft="updateIntakeDraft"
        @submit="submitIntakeDraft"
      />

      <DashboardPage v-else />
    </section>
  </main>
</template>
