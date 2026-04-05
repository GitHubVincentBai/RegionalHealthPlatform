export function createMockElder(overrides = {}) {
  return {
    elderId: "E-1001",
    elderCode: "HPT-EL-001",
    fullName: "张桂兰",
    gender: "女",
    age: 82,
    riskLevel: "高风险",
    status: "已入住",
    currentStayStatus: "checked_in",
    station: "龙湖邻里中心",
    room: "A-301",
    bed: "A-301-02",
    family: "张伟",
    familyRelation: "子女",
    familyPhone: "13800000001",
    familyContacts: [
      {
        family_name: "张伟",
        relation_type: "子女",
        phone: "13800000001",
        is_primary_contact: true,
      },
    ],
    checkInDate: "2025-03-12",
    note: "血压波动较大，优先级较高。",
    source: "mock",
    ...overrides,
  };
}

export function elderArchiveModel() {
  return {
    summary: {
      total: 24,
      checkedIn: 18,
      waitingCheckIn: 4,
      highRisk: 6,
    },
    elders: [
      createMockElder(),
      createMockElder({
        elderId: "E-1002",
        elderCode: "HPT-EL-002",
        fullName: "李秀英",
        age: 76,
        riskLevel: "中风险",
        status: "待入住",
        currentStayStatus: "pre_admission",
        station: "和平街社区站点",
        room: "B-208",
        bed: "B-208-01",
        family: "李强",
        familyRelation: "子女",
        familyPhone: "13800000002",
        familyContacts: [
          {
            family_name: "李强",
            relation_type: "子女",
            phone: "13800000002",
            is_primary_contact: true,
          },
        ],
        checkInDate: "待安排",
        note: "已完成资料审核，待床位确认。",
      }),
      createMockElder({
        elderId: "E-1003",
        elderCode: "HPT-EL-003",
        fullName: "王德福",
        gender: "男",
        age: 88,
        station: "三好街站点",
        room: "C-108",
        bed: "C-108-03",
        family: "王敏",
        familyRelation: "女儿",
        familyPhone: "13800000003",
        familyContacts: [
          {
            family_name: "王敏",
            relation_type: "女儿",
            phone: "13800000003",
            is_primary_contact: true,
          },
        ],
        checkInDate: "2025-04-01",
        note: "晚间需重点巡视。",
      }),
    ],
  };
}

export function createElderDraft() {
  return {
    elderId: "",
    elderCode: "",
    fullName: "",
    gender: "女",
    age: 80,
    riskLevel: "中风险",
    station: "龙湖邻里中心",
    checkInStatus: "待入住",
    room: "",
    bed: "",
    familyName: "",
    familyRelation: "子女",
    familyPhone: "",
    checkInDate: "",
    note: "",
  };
}
