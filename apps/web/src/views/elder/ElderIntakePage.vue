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
  successMessage: {
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
  validationErrors: {
    type: Object,
    default: () => ({}),
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
        <p class="summary">
          表单按“长者档案、家属关系、入住信息、房间床位”四组最小对象建模，便于继续接入真实 API、扩展合同与费用流程。
        </p>
      </div>
      <div class="detail-hero__tags">
        <span class="pill pill-accent">{{ dataSource === "mock" ? "Mock Fallback" : "elder-service" }}</span>
        <span class="pill">入住基础信息</span>
        <span class="pill">家属关系</span>
      </div>
    </article>

    <section class="intake-layout">
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
        <p v-if="successMessage" class="info-banner info-banner--success field-span-2">{{ successMessage }}</p>

        <div class="form-section field-span-2">
          <div class="form-section__head">
            <h3>长者基础档案</h3>
            <p>覆盖档案编号、身份信息、联系方式和风险等级。</p>
          </div>
          <div class="form-grid">
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
              <small v-if="validationErrors.fullName" class="field-error">{{ validationErrors.fullName }}</small>
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
              出生日期
              <input
                :value="draft.birthDate"
                type="date"
                @input="emit('update:draft', { ...draft, birthDate: $event.target.value })"
              />
            </label>
            <label>
              长者电话
              <input
                :value="draft.phone"
                type="tel"
                placeholder="13600000000"
                @input="emit('update:draft', { ...draft, phone: $event.target.value })"
              />
            </label>
            <label>
              身份证号
              <input
                :value="draft.idCard"
                type="text"
                placeholder="210102194302120018"
                @input="emit('update:draft', { ...draft, idCard: $event.target.value })"
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
          </div>
        </div>

        <div class="form-section field-span-2">
          <div class="form-section__head">
            <h3>站点与入住信息</h3>
            <p>承接站点归属、入住状态、房间床位和基础备注。</p>
          </div>
          <div class="form-grid">
            <label>
              站点名称
              <input
                :value="draft.station"
                type="text"
                @input="emit('update:draft', { ...draft, station: $event.target.value })"
              />
            </label>
            <label>
              站点编码
              <input
                :value="draft.stationId"
                type="text"
                placeholder="station-longhu"
                @input="emit('update:draft', { ...draft, stationId: $event.target.value })"
              />
              <small v-if="validationErrors.stationId" class="field-error">{{ validationErrors.stationId }}</small>
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
              预计入住日期
              <input
                :value="draft.checkInDate"
                type="date"
                @input="emit('update:draft', { ...draft, checkInDate: $event.target.value })"
              />
              <small v-if="validationErrors.checkInDate" class="field-error">{{ validationErrors.checkInDate }}</small>
            </label>
            <label>
              房间
              <input
                :value="draft.room"
                type="text"
                placeholder="A-301"
                @input="emit('update:draft', { ...draft, room: $event.target.value })"
              />
              <small v-if="validationErrors.room" class="field-error">{{ validationErrors.room }}</small>
            </label>
            <label>
              床位
              <input
                :value="draft.bed"
                type="text"
                placeholder="A-301-02"
                @input="emit('update:draft', { ...draft, bed: $event.target.value })"
              />
              <small v-if="validationErrors.bed" class="field-error">{{ validationErrors.bed }}</small>
            </label>
            <label class="field-span-2">
              入住备注
              <textarea
                :value="draft.note"
                rows="4"
                @input="emit('update:draft', { ...draft, note: $event.target.value })"
              />
            </label>
          </div>
        </div>

        <div class="form-section field-span-2">
          <div class="form-section__head">
            <h3>家属关系</h3>
            <p>首批只保留主联系人，但字段已可扩展为 family_contacts 列表。</p>
          </div>
          <div class="form-grid">
            <label>
              家属姓名
              <input
                :value="draft.familyName"
                type="text"
                @input="emit('update:draft', { ...draft, familyName: $event.target.value })"
              />
              <small v-if="validationErrors.familyName" class="field-error">{{ validationErrors.familyName }}</small>
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
              <small v-if="validationErrors.familyPhone" class="field-error">{{ validationErrors.familyPhone }}</small>
            </label>
          </div>
        </div>

        <div class="form-actions field-span-2">
          <button type="submit" class="action-button" :disabled="submitting">
            {{ submitting ? "提交中..." : "保存入住草稿" }}
          </button>
          <span class="toolbar-hint">
            表单会映射到 elder-service 的 `POST /elders`，并通过 `station_id / family_contacts / stay_info` 完成前后端对接。
          </span>
        </div>
      </form>

      <aside class="intake-aside">
        <article class="detail-panel detail-panel--accent">
          <h3>实时预览</h3>
          <dl class="detail-dl">
            <div>
              <dt>长者姓名</dt>
              <dd>{{ draft.fullName || "待填写" }}</dd>
            </div>
            <div>
              <dt>站点</dt>
              <dd>{{ draft.station || draft.stationId || "待填写" }}</dd>
            </div>
            <div>
              <dt>入住状态</dt>
              <dd>{{ draft.checkInStatus }}</dd>
            </div>
            <div>
              <dt>床位安排</dt>
              <dd>{{ draft.room || "待安排" }} / {{ draft.bed || "待安排" }}</dd>
            </div>
            <div>
              <dt>主联系人</dt>
              <dd>{{ draft.familyName || "待填写" }}</dd>
            </div>
          </dl>
        </article>

        <article class="detail-panel">
          <h3>首批验收点</h3>
          <ul class="workbench-points">
            <li>支持创建长者档案</li>
            <li>支持最小入住信息入参</li>
            <li>支持家属关系与主联系人</li>
            <li>为合同、费用、护理计划预留扩展点</li>
          </ul>
        </article>

        <article class="detail-panel">
          <h3>填写提醒</h3>
          <ul class="workbench-points">
            <li>已入住长者必须填写房间、床位和入住日期</li>
            <li>床位前必须先有房间</li>
            <li>站点编码和主联系人为首批必填字段</li>
            <li>隐私字段只展示最小必要信息</li>
          </ul>
        </article>
      </aside>
    </section>
  </section>
</template>
