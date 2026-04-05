<script setup>
import { computed } from "vue";
import SectionCard from "../../components/SectionCard.vue";
import StatCard from "../../components/StatCard.vue";

const props = defineProps({
  summary: {
    type: Object,
    required: true,
  },
  elders: {
    type: Array,
    required: true,
  },
  selectedElderId: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(["select-elder", "create-draft"]);

const selectedElder = computed(
  () => props.elders.find((elder) => elder.elderId === props.selectedElderId) ?? props.elders[0],
);
</script>

<template>
  <section class="page-stack">
    <section class="metrics-grid metrics-grid-archive" aria-label="长者档案指标">
      <StatCard
        label="档案总数"
        :value="summary.total"
        helper="覆盖档案、入住与家属关系"
      />
      <StatCard label="已入住" :value="summary.checkedIn" helper="当前可服务长者" />
      <StatCard label="待入住" :value="summary.waitingCheckIn" helper="待安排床位或资料完善" />
      <StatCard label="高风险" :value="summary.highRisk" helper="需重点关注" />
    </section>

    <section class="content-grid content-grid-wide">
      <SectionCard title="长者档案列表" description="用于筛选、查看和进入详情。">
        <div class="archive-toolbar">
          <button type="button" class="action-button" @click="emit('create-draft')">
            新建长者档案
          </button>
          <span class="toolbar-hint">当前为本地 mock 数据，后续可直接接真实 API。</span>
        </div>

        <ul class="archive-list">
          <li
            v-for="elder in elders"
            :key="elder.elderId"
            class="archive-row"
            :class="{ 'is-active': elder.elderId === selectedElderId }"
            @click="emit('select-elder', elder.elderId)"
          >
            <div>
              <strong>{{ elder.fullName }}</strong>
              <p>{{ elder.elderCode }} · {{ elder.gender }} · {{ elder.age }} 岁</p>
            </div>
            <div class="archive-row__meta">
              <span class="tag tag-p2">{{ elder.riskLevel }}</span>
              <span class="archive-row__status">{{ elder.status }}</span>
            </div>
          </li>
        </ul>
      </SectionCard>

      <SectionCard title="入住说明" description="预留床位、家属和签约字段。">
        <div class="detail-grid">
          <div>
            <span class="detail-label">站点</span>
            <strong>{{ selectedElder.station }}</strong>
          </div>
          <div>
            <span class="detail-label">床位</span>
            <strong>{{ selectedElder.bed }}</strong>
          </div>
          <div>
            <span class="detail-label">家属</span>
            <strong>{{ selectedElder.family }}</strong>
            <small>{{ selectedElder.familyRelation }}</small>
          </div>
        </div>
      </SectionCard>
    </section>
  </section>
</template>
