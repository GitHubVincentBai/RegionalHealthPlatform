<script setup>
import StatCard from "../../components/StatCard.vue";
import SectionCard from "../../components/SectionCard.vue";
import { dashboardModel } from "../../modules/dashboard/model.js";
import { formatCount, formatPercent } from "../../shared/utils/format.js";

const { stats, tasks, alerts, services, releases } = dashboardModel();
</script>

<template>
  <section class="page-stack">
    <section class="metrics-grid" aria-label="关键指标">
      <StatCard v-for="stat in stats" :key="stat.label" :stat="stat" />
    </section>

    <section class="content-grid">
      <SectionCard title="今日待办" description="优先级、状态与责任人一目了然。">
        <ul class="list">
          <li v-for="task in tasks" :key="task.title" class="list-item">
            <div>
              <strong>{{ task.title }}</strong>
              <p>{{ task.owner }} · {{ task.deadline }}</p>
            </div>
            <span class="tag" :class="`tag-${task.priority.toLowerCase()}`">
              {{ task.priority }}
            </span>
          </li>
        </ul>
      </SectionCard>

      <SectionCard title="告警概览" description="突出异常、处置进度和升级状态。">
        <ul class="stack">
          <li v-for="alert in alerts" :key="alert.name" class="stack-item">
            <div>
              <strong>{{ alert.name }}</strong>
              <p>{{ alert.site }} · {{ alert.status }}</p>
            </div>
            <span class="metric">{{ formatPercent(alert.ratio) }}</span>
          </li>
        </ul>
      </SectionCard>
    </section>

    <section class="content-grid content-grid-wide">
      <SectionCard title="服务分层" description="用清晰的分层卡片保留组件化拆分空间。">
        <div class="service-list">
          <article v-for="service in services" :key="service.name" class="service-card">
            <div class="service-card__head">
              <h3>{{ service.name }}</h3>
              <span class="badge">{{ service.stage }}</span>
            </div>
            <p>{{ service.summary }}</p>
            <small>{{ formatCount(service.touchpoints) }}</small>
          </article>
        </div>
      </SectionCard>

      <SectionCard title="交付节奏" description="将设计、开发、测试和发布拆成可追踪的步骤。">
        <ol class="timeline">
          <li v-for="(release, index) in releases" :key="release.name" class="timeline-item">
            <span class="timeline-index">{{ index + 1 }}</span>
            <div>
              <strong>{{ release.name }}</strong>
              <p>{{ release.detail }}</p>
            </div>
          </li>
        </ol>
      </SectionCard>
    </section>
  </section>
</template>
