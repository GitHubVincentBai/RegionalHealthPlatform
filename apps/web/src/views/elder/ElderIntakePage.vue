<script setup>
defineProps({
  draft: {
    type: Object,
    required: true,
  },
  submitting: {
    type: Boolean,
    default: false,
  },
  errorMessage: {
    type: String,
    default: "",
  },
  dataSource: {
    type: String,
    default: "api",
  },
  syncWarning: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["back", "update:draft", "submit"]);
</script>

<template>
  <section class="page-stack">
    <article class="detail-hero">
      <div>
        <p class="eyebrow">入住办理</p>
        <h2>长者档案创建与入住基础信息</h2>
        <p class="summary">表单先保留最小字段，方便后续直接接入真实 API 和审批流程。</p>
      </div>
      <div class="detail-hero__tags">
        <span class="pill pill-accent">{{ dataSource === "mock" ? "Mock Fallback" : "elder-service" }}</span>
        <span class="pill">入住基础信息</span>
      </div>
    </article>

    <form class="intake-form" @submit.prevent="emit('submit')">
      <div class="form-actions field-span-2 form-actions--top">
        <button type="button" class="action-button action-button--ghost" @click="emit('back')">
          返回列表
        </button>
        <span class="toolbar-hint">
          {{
            dataSource === "mock"
              ? "当前允许 mock 兜底保存，页面会明确标记未命中 elder-service。"
              : "当前直接提交到 elder-service 的 POST /elders。"
          }}
        </span>
      </div>
      <p v-if="syncWarning" class="info-banner info-banner--warning field-span-2">{{ syncWarning }}</p>
      <p v-if="errorMessage" class="info-banner info-banner--danger field-span-2">{{ errorMessage }}</p>
      <label>
        档案编号
        <input
          :value="draft.elderCode"
          type="text"
          placeholder="HPT-EL-004"
          @input="emit('update:draft', { ...draft, elderCode: $event.target.value })"
        />
      </label>
      <label>
        姓名
        <input
          :value="draft.fullName"
          type="text"
          placeholder="请输入长者姓名"
          @input="emit('update:draft', { ...draft, fullName: $event.target.value })"
        />
      </label>
      <label>
        性别
        <select
          :value="draft.gender"
          @change="emit('update:draft', { ...draft, gender: $event.target.value })"
        >
          <option>女</option>
          <option>男</option>
        </select>
      </label>
      <label>
        年龄
        <input
          :value="draft.age"
          type="number"
          min="0"
          @input="emit('update:draft', { ...draft, age: Number($event.target.value) })"
        />
      </label>
      <label>
        风险等级
        <select
          :value="draft.riskLevel"
          @change="emit('update:draft', { ...draft, riskLevel: $event.target.value })"
        >
          <option>低风险</option>
          <option>中风险</option>
          <option>高风险</option>
        </select>
      </label>
      <label>
        站点
        <input
          :value="draft.station"
          type="text"
          @input="emit('update:draft', { ...draft, station: $event.target.value })"
        />
      </label>
      <label>
        入住状态
        <select
          :value="draft.checkInStatus"
          @change="emit('update:draft', { ...draft, checkInStatus: $event.target.value })"
        >
          <option>待入住</option>
          <option>已入住</option>
        </select>
      </label>
      <label>
        房间
        <input
          :value="draft.room"
          type="text"
          placeholder="A-301"
          @input="emit('update:draft', { ...draft, room: $event.target.value })"
        />
      </label>
      <label>
        床位
        <input
          :value="draft.bed"
          type="text"
          placeholder="A-301-02"
          @input="emit('update:draft', { ...draft, bed: $event.target.value })"
        />
      </label>
      <label>
        家属姓名
        <input
          :value="draft.familyName"
          type="text"
          @input="emit('update:draft', { ...draft, familyName: $event.target.value })"
        />
      </label>
      <label>
        家属关系
        <input
          :value="draft.familyRelation"
          type="text"
          @input="emit('update:draft', { ...draft, familyRelation: $event.target.value })"
        />
      </label>
      <label>
        家属电话
        <input
          :value="draft.familyPhone"
          type="tel"
          placeholder="13800000000"
          @input="emit('update:draft', { ...draft, familyPhone: $event.target.value })"
        />
      </label>
      <label>
        预计入住日期
        <input
          :value="draft.checkInDate"
          type="date"
          @input="emit('update:draft', { ...draft, checkInDate: $event.target.value })"
        />
      </label>
      <label class="field-span-2">
        入住备注
        <textarea
          :value="draft.note"
          rows="4"
          @input="emit('update:draft', { ...draft, note: $event.target.value })"
        />
      </label>
      <div class="form-actions field-span-2">
        <button type="submit" class="action-button" :disabled="submitting">
          {{ submitting ? "提交中..." : "保存入住草稿" }}
        </button>
        <span class="toolbar-hint">表单会映射到 elder-service 的最小创建字段，额外前端字段保持占位展示。</span>
      </div>
    </form>
  </section>
</template>
