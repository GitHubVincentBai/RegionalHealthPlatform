# 长者档案与入住测试矩阵

## 1. 目标

本测试矩阵用于覆盖“长者档案 / 入住”首批业务闭环，依据 [docs/product/Elder入住首批任务包.md](/Users/baizhiwen/MICROWARE/Git/RegionalHealthPlatform/docs/product/Elder入住首批任务包.md) 编制。

覆盖范围：

- 长者档案创建、查询、列表展示
- 入住基础信息录入与展示
- 家属关系最小字段校验
- 床位与房间关联
- 前后端联调的最小冒烟路径

## 2. 测试原则

- 优先验证业务闭环最小可行性，不追求一次性覆盖完整入住系统
- 先验证字段、状态和边界，再验证页面与接口联动
- 自动化优先覆盖高频和高风险路径
- 不把“页面展示成功”视为业务通过，必须至少包含字段校验和状态流转

## 3. 最小用例清单

### 3.1 前端最小用例

| 编号 | 场景 | 前置条件 | 操作 | 预期结果 | 自动化优先级 |
|---|---|---|---|---|---|
| FE-01 | 长者档案列表展示 | 有至少 1 条长者档案数据 | 打开长者档案列表页 | 列表正常渲染，包含姓名、风险等级、入住状态 | P0 |
| FE-02 | 长者档案详情查看 | 选中某一条档案 | 进入详情页 | 可看到基础信息、家属关系、入住信息区块 | P0 |
| FE-03 | 长者档案创建表单 | 打开创建页 | 填写必填项并提交 | 表单通过校验，提交入口可用 | P0 |
| FE-04 | 入住信息展示 | 档案包含入住字段 | 打开详情页 | 入住日期、床位、房间、状态清晰展示 | P1 |
| FE-05 | 表单缺失必填项 | 清空必填字段 | 提交表单 | 前端阻断并显示明确错误信息 | P0 |

### 3.2 后端最小用例

| 编号 | 场景 | 前置条件 | 操作 | 预期结果 | 自动化优先级 |
|---|---|---|---|---|---|
| BE-01 | 创建长者档案成功 | 请求包含 elder_id、elder_code、姓名、风险等级 | 调用创建接口 | 返回成功，档案可查询 | P0 |
| BE-02 | 长者档案重复创建 | 已存在相同 elder_id | 再次调用创建接口 | 返回冲突或等价错误 | P0 |
| BE-03 | 查询长者列表 | 仓储中已有多条档案 | 调用列表接口 | 返回列表数据，顺序和数量正确 | P0 |
| BE-04 | 查询长者详情 | 已存在目标档案 | 调用详情接口 | 返回完整档案与入住字段 | P0 |
| BE-05 | 必填字段缺失 | elder_id 或姓名缺失 | 调用创建接口 | 返回校验错误 | P0 |
| BE-06 | 入住字段最小校验 | 提交入住日期、床位或房间信息 | 调用创建接口 | 入住字段被接受或按规则拒绝 | P1 |

### 3.3 联调用例

| 编号 | 场景 | 前置条件 | 操作 | 预期结果 | 自动化优先级 |
|---|---|---|---|---|---|
| IT-01 | 前端创建档案到后端写入 | 前后端均可运行 | 从前端提交创建请求 | 后端成功落库，前端展示成功态 | P0 |
| IT-02 | 前端列表刷新后可见新档案 | 已完成创建 | 返回列表页刷新 | 新档案在列表中可见 | P0 |
| IT-03 | 前端详情页读取入住信息 | 档案包含入住字段 | 打开详情页 | 入住信息与后端返回一致 | P1 |
| IT-04 | 家属关系字段映射 | 档案包含家属信息 | 查看详情 | 家属名称、关系、主联系人标识正确展示 | P1 |

### 3.4 回归用例

| 编号 | 场景 | 覆盖目的 | 自动化优先级 |
|---|---|---|---|
| RG-01 | 长者创建后立即查询详情 | 防止创建与查询字段不一致 | P0 |
| RG-02 | 入住字段新增后列表仍可渲染 | 防止字段扩展破坏列表页 | P0 |
| RG-03 | 家属关系字段缺省兼容 | 防止历史数据异常 | P1 |
| RG-04 | 非法输入被拦截 | 防止校验失效 | P0 |

## 4. 自动化优先级

### P0

必须自动化覆盖的最小集合：

- 长者档案创建成功
- 长者档案重复创建失败
- 长者档案详情查询
- 表单必填项校验
- 前后端联调用例中的创建与查询主链路

### P1

建议自动化覆盖：

- 入住信息展示
- 家属关系字段展示
- 列表刷新与筛选
- 回归用例中的兼容性校验

### P2

视排期补充：

- 异常输入的细粒度错误提示
- 更复杂的入住状态机
- 批量导入、批量迁移、历史数据修复场景

## 5. 测试数据建议

- 长者基础档案：至少 1 条正常数据、1 条缺失必填字段数据、1 条重复数据
- 家属关系：至少 1 条主联系人、1 条普通联系人
- 入住信息：至少 1 条已入住、1 条待入住、1 条未分配床位
- 床位信息：至少 1 个有效床位、1 个空床位、1 个无效床位

## 6. 自动化落点建议

- 前端可优先使用组件级或页面级快照 + 交互断言
- 后端可优先使用应用层单测与 HTTP 层接口测试
- 联调阶段可优先做“创建后查询”最小冒烟
- 回归阶段可优先跑 P0 集合，确保档案主链路不退化

## 6.1 P0 用例到实际资产映射

本轮已把 Elder 入住 MVP 的最小冒烟入口接入仓库统一命令，避免 `make` 只能跳过却无法执行真实资产。

| 编号 | 实际文件 | 覆盖说明 | 执行命令 |
|---|---|---|---|
| SMK-00 | `tests/integration/elder_mvp_smoke.sh` | 仓库统一 smoke 入口，桥接到真实 P0 主链路脚本，供 `make test-elder-integration-smoke` 调用 | `make test-elder-integration-smoke` |
| SMK-01 | `tests/integration/elder_create_query_smoke.sh` | 串联后端服务层与前端适配层的 P0 冒烟，覆盖创建档案后可查询列表/详情的主链路 | `bash tests/integration/elder_create_query_smoke.sh` |

| 编号 | 实际文件 | 覆盖说明 | 执行命令 |
|---|---|---|---|
| FE-01 | `apps/web/src/api/adapters/elder-service/flow.spec.mjs` | 通过 `loadArchive()` 断言新建后列表可见姓名、入住状态 | `cd apps/web && node --test ./src/api/adapters/elder-service/flow.spec.mjs` |
| FE-02 | `apps/web/src/api/adapters/elder-service/flow.spec.mjs` | 通过 `getElder()` 断言详情包含入住与家属信息 | `cd apps/web && node --test ./src/api/adapters/elder-service/flow.spec.mjs` |
| FE-03 | `apps/web/src/api/adapters/elder-service/archiveService.spec.mjs` | 断言创建草稿可被转换并提交为 elder-service 兼容载荷 | `cd apps/web && node --test ./src/api/adapters/elder-service/archiveService.spec.mjs` |
| FE-05 | 暂无自动化资产 | 当前前端页面级必填错误提示尚未形成可执行断言入口，需要 FrontAgent 补页面交互测试基座 | 暂无 |
| BE-01 | `services/python/elder-service/tests/test_service.py` | 应用层最小冒烟覆盖创建后可查列表/详情主链路，断言入住与家属字段不丢失 | `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_service.ElderServiceTest.test_create_list_and_fetch_profile_smoke` |
| BE-02 | `services/python/elder-service/tests/test_service.py` | 应用层覆盖重复创建抛出 `ElderProfileAlreadyExistsError` | `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_service.ElderServiceTest.test_duplicate_profile_rejected` |
| BE-03 | `services/python/elder-service/tests/test_service.py` | 应用层覆盖列表查询、过滤与分页 | `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_service.ElderServiceTest.test_list_profiles_supports_filters_and_pagination` |
| BE-04 | `services/python/elder-service/tests/test_service.py` | 应用层详情查询返回完整档案字段 | `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_service.ElderServiceTest.test_create_list_and_fetch_profile_smoke` |
| BE-05 | `services/python/elder-service/tests/test_service.py` | 应用层覆盖 `elder_id`、`full_name` 缺失触发校验错误 | `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_service.ElderServiceTest.test_required_fields_raise_value_error` |
| IT-01 | `services/python/elder-service/tests/test_service.py` | 后端最小冒烟资产，覆盖创建后立即查询列表与详情 | `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_service.ElderServiceTest.test_create_list_and_fetch_profile_smoke` |
| IT-02 | `apps/web/src/api/adapters/elder-service/flow.spec.mjs` | 前端服务层冒烟，覆盖创建后刷新列表即可看到新档案 | `cd apps/web && node --test ./src/api/adapters/elder-service/flow.spec.mjs` |
| RG-01 | `services/python/elder-service/tests/test_service.py` | 防止创建接口与查询接口字段脱节 | `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_service.ElderServiceTest.test_create_list_and_fetch_profile_smoke` |
| RG-02 | `apps/web/src/api/adapters/elder-service/archiveService.spec.mjs` | 防止入住字段存在时档案列表映射退化 | `cd apps/web && node --test ./src/api/adapters/elder-service/archiveService.spec.mjs` |
| RG-04 | `services/python/elder-service/tests/test_service.py` | 防止必填校验失效 | `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_service.ElderServiceTest.test_required_fields_raise_value_error` |

## 6.2 补充 HTTP 资产

以下真实 HTTP 资产已补齐在仓库内，适合依赖安装完整时追加执行：

| 编号 | 实际文件 | 覆盖说明 | 执行命令 |
|---|---|---|---|
| HTTP-01 | `services/python/elder-service/tests/test_http.py` | 真实 HTTP 接口覆盖创建后可查列表/详情主链路 | `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_http.ElderHttpApiTest.test_create_list_and_fetch_profile` |
| HTTP-02 | `services/python/elder-service/tests/test_http.py` | 真实 HTTP 接口覆盖重复创建返回 `409` | `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_http.ElderHttpApiTest.test_duplicate_profile_returns_409` |
| HTTP-03 | `services/python/elder-service/tests/test_http.py` | 真实 HTTP 接口覆盖列表查询、过滤与分页 | `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_http.ElderHttpApiTest.test_list_endpoint_supports_filters_and_pagination` |
| HTTP-04 | `services/python/elder-service/tests/test_http.py` | 真实 HTTP 接口覆盖必填字段缺失返回 `422` | `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_http.ElderHttpApiTest.test_missing_required_fields_return_422` |

## 6.3 本轮执行记录

执行时间：

- 2026-04-05

执行命令：

- `make test-elder-integration-smoke`
- `bash tests/integration/elder_create_query_smoke.sh`
- `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_service.ElderServiceTest.test_create_list_and_fetch_profile_smoke tests.test_service.ElderServiceTest.test_duplicate_profile_rejected tests.test_service.ElderServiceTest.test_required_fields_raise_value_error tests.test_service.ElderServiceTest.test_list_profiles_supports_filters_and_pagination`
- `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_http`
- `cd apps/web && node --test ./src/api/adapters/elder-service/flow.spec.mjs ./src/api/adapters/elder-service/archiveService.spec.mjs`

执行目的：

- 验证后端最小冒烟资产已覆盖创建后列表/详情查询
- 验证真实 HTTP 资产在依赖不完整时会显式跳过，不再因导入失败阻断测试发现
- 验证前端 elder-service 适配层已覆盖创建后列表刷新与详情读取

执行结果：

- `make test-elder-integration-smoke`
  结果：已补齐统一入口后通过；`make` 现已执行 `tests/integration/elder_mvp_smoke.sh`，不再因找不到资产而跳过
- `bash tests/integration/elder_create_query_smoke.sh`
  结果：通过；聚合验证后端创建后查列表/详情，以及前端适配层创建后列表刷新与详情读取主链路
- `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_service.ElderServiceTest.test_create_list_and_fetch_profile_smoke tests.test_service.ElderServiceTest.test_duplicate_profile_rejected tests.test_service.ElderServiceTest.test_required_fields_raise_value_error tests.test_service.ElderServiceTest.test_list_profiles_supports_filters_and_pagination`
  结果：通过（4/4）
- `cd services/python/elder-service && PYTHONPATH=src python3 -m unittest tests.test_http`
  结果：跳过（0 失败，7 跳过）；当前执行环境缺少 `fastapi` 运行依赖，已显式标注为环境依赖
- `cd apps/web && node --test ./src/api/adapters/elder-service/flow.spec.mjs ./src/api/adapters/elder-service/archiveService.spec.mjs`
  结果：通过（7/7）
- `make verify`
  结果：阻塞；`lint-web` 已通过，但 `lint-python-elder-service` 在无外网环境下同步 Python 依赖失败，`pip` 无法拉取 `setuptools`

## 7. 未覆盖风险

- 入住状态机未完全成型前，状态流转的完整性无法一次覆盖
- 如果后续引入真实数据库或认证层，当前测试数据可能需要重新适配
- 若前端正式路由和接口契约进一步细化，本矩阵需要同步更新字段映射

## 8. 备注

本文件当前同时承担两部分职责：

- 维护 Elder 入住首批测试矩阵、P0 资产映射和执行命令
- 记录本轮已实际执行的最小验证结果；后续若资产或结果发生变化，应同步更新本节，避免“文档有矩阵但仓库无可执行结果”
