<script setup>
const emit = defineEmits(["back"]);

defineProps({
  elder: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <section class="page-stack">
    <article class="detail-hero">
      <div>
        <p class="eyebrow">长者详情</p>
        <h2>{{ elder.fullName }}</h2>
        <p class="summary">
          {{ elder.elderCode }} · {{ elder.gender }} · {{ elder.age }} 岁 · {{ elder.status }}
        </p>
      </div>
      <div class="detail-hero__tags">
        <span class="pill pill-accent">{{ elder.riskLevel }}</span>
        <span class="pill">{{ elder.station }}</span>
      </div>
    </article>

    <div class="inline-actions">
      <button type="button" class="action-button action-button--ghost" @click="emit('back')">
        返回档案列表
      </button>
    </div>

    <section class="content-grid">
      <article class="detail-panel">
        <h3>基础信息</h3>
        <dl class="detail-dl">
          <div>
            <dt>档案编号</dt>
            <dd>{{ elder.elderCode }}</dd>
          </div>
          <div>
            <dt>入住时间</dt>
            <dd>{{ elder.checkInDate }}</dd>
          </div>
          <div>
            <dt>床位</dt>
            <dd>{{ elder.bed }}</dd>
          </div>
          <div>
            <dt>风险等级</dt>
            <dd>{{ elder.riskLevel }}</dd>
          </div>
        </dl>
      </article>

      <article class="detail-panel">
        <h3>家属关系</h3>
        <dl class="detail-dl">
          <div>
            <dt>家属姓名</dt>
            <dd>{{ elder.family }}</dd>
          </div>
          <div>
            <dt>关系</dt>
            <dd>{{ elder.familyRelation }}</dd>
          </div>
          <div>
            <dt>备注</dt>
            <dd>{{ elder.note }}</dd>
          </div>
        </dl>
      </article>
    </section>
  </section>
</template>
