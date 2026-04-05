<script setup>
import { computed, reactive, ref } from "vue";
import AppHeader from "./components/AppHeader.vue";
import AppNav from "./components/AppNav.vue";
import DashboardPage from "./views/dashboard/DashboardPage.vue";
import ElderArchivePage from "./views/elder/ElderArchivePage.vue";
import ElderDetailPage from "./views/elder/ElderDetailPage.vue";
import ElderIntakePage from "./views/elder/ElderIntakePage.vue";
import { elderArchiveModel, createElderDraft } from "./modules/elder/mock.js";
import { useHashView } from "./composables/useHashView.js";

const { view, navigate } = useHashView("dashboard");
const appState = reactive(elderArchiveModel());
const activeElderId = ref(appState.elders[0].elderId);
const intakeDraft = ref(createElderDraft());

const navItems = [
  { key: "dashboard", label: "总览", hint: "控制台" },
  { key: "elder-list", label: "长者档案", hint: "列表与详情" },
  { key: "elder-intake", label: "入住办理", hint: "创建草稿" },
];

const currentElder = computed(
  () => appState.elders.find((elder) => elder.elderId === activeElderId.value) ?? appState.elders[0],
);

const pageTitle = computed(() => {
  if (view.value === "elder-list") {
    return "长者档案工作台";
  }

  if (view.value === "elder-intake") {
    return "长者入住办理";
  }

  return "区域康养平台 Web 管理端";
});

const pageDescription = computed(() => {
  if (view.value === "elder-list") {
    return "围绕长者档案、家属关系、入住信息和床位关联的首批业务入口。";
  }

  if (view.value === "elder-intake") {
    return "先落地创建档案与入住草稿，为后续 FastAPI 联调预留稳定表单结构。";
  }

  return "当前是 Vue 版首批骨架，聚焦控制台、长者档案、入住办理与运营总览。";
});

const selectElder = (elderId) => {
  activeElderId.value = elderId;
  navigate("elder-detail");
};

const resetIntakeDraft = () => {
  intakeDraft.value = createElderDraft();
  navigate("elder-intake");
};

const updateIntakeDraft = (nextDraft) => {
  intakeDraft.value = nextDraft;
};

const submitIntakeDraft = () => {
  const nextId = `E-${String(appState.elders.length + 1001)}`;

  appState.summary.total += 1;
  appState.summary.waitingCheckIn += 1;
  appState.elders.unshift({
    elderId: nextId,
    elderCode: intakeDraft.value.elderCode || `HPT-EL-${appState.elders.length + 1}`,
    fullName: intakeDraft.value.fullName || "未命名长者",
    gender: intakeDraft.value.gender,
    age: intakeDraft.value.age,
    riskLevel: intakeDraft.value.riskLevel,
    status: "待入住",
    station: intakeDraft.value.station,
    room: intakeDraft.value.room || "待安排",
    bed: intakeDraft.value.bed || "待安排",
    family: intakeDraft.value.familyName || "待补充",
    familyRelation: intakeDraft.value.familyRelation || "待补充",
    checkInDate: intakeDraft.value.checkInDate || "待安排",
    note: intakeDraft.value.note || "已保存入住草稿。",
  });

  activeElderId.value = nextId;
  navigate("elder-detail");
};
</script>

<template>
  <main class="app-shell">
    <section class="shell-frame">
      <AppHeader :title="pageTitle" :description="pageDescription" />

      <AppNav :current-view="view" :items="navItems" @navigate="navigate" />

      <DashboardPage v-if="view === 'dashboard'" />

      <ElderArchivePage
        v-else-if="view === 'elder-list'"
        :summary="appState.summary"
        :elders="appState.elders"
        :selected-elder-id="activeElderId"
        @select-elder="selectElder"
        @create-draft="resetIntakeDraft"
      />

      <ElderDetailPage
        v-else-if="view === 'elder-detail'"
        :elder="currentElder"
        @back="navigate('elder-list')"
      />

      <ElderIntakePage
        v-else-if="view === 'elder-intake'"
        :draft="intakeDraft"
        @back="navigate('elder-list')"
        @update:draft="updateIntakeDraft"
        @submit="submitIntakeDraft"
      />

      <DashboardPage v-else />
    </section>
  </main>
</template>
