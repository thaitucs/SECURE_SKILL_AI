# SECURE_CHECK

**Security audit · Security score · Frontend/Backend file sorting · Project restructuring ·
Code splitting · Email/phone anti-spam — for any app, web app or website, with any AI.**

**Kiểm tra bảo mật · Chấm điểm bảo mật · Phân loại file Frontend/Backend · Sắp xếp lại dự án ·
Tách code · Chống spam email/số điện thoại — cho mọi app, web app, website, với mọi AI.**

- [English](#english)
- [Tiếng Việt](#tiếng-việt)

---

# English

## 1. What SECURE_CHECK does

When you run SECURE_CHECK on a project, the AI will:

1. **Read and map the whole project** - type (website, web app, API, mobile, desktop,
   full-stack), stack, entry points, where it is deployed.
2. **Classify every file** - Frontend, Backend, Database, File storage, Shared, Config,
   Private (must never be public), Generated, Docs, Test - and flag problems such as
   secrets in frontend code, business logic in the browser, files that should be removed.
3. **Audit security** - leaked keys and passwords, files that must not be public, access
   control, injection (SQL, XSS, command, SSRF...), authentication, uploads and storage,
   configuration, rate limiting, dependencies, mobile/desktop specifics.
4. **Score security** from 0 to 100 with a grade (A-F), per category, plus the projected
   score after the proposed fixes.
5. **Propose a clean structure** and **split messy code** into clear modules, each with one
   job, so the project is easier to develop later. No fixed line limit - files are split
   by responsibility, adapted to the project.
6. **Protect emails and phone numbers** shown on the site/app from spam bots, and protect
   forms and OTP/SMS from abuse.
7. Write a **short, highlighted plan** (`SECURE_CHECK_PLAN.txt`) and **wait for your
   approval**. Nothing changes until you approve specific items.

## 2. How it works

```
 You: "Run SECURE_CHECK on this project"
            |
            v
 1 Safety & mode ......... read-only by default, checks git/backup
 2 Discovery ............. stack, entry points, deploy folder, architecture status
 3 Classification ........ every file -> label + flags + reason  -> FILE_MAP.md
 4 Security audit ........ checklists + scanners, verified        -> SECURITY_REPORT.md
 5 Security score ........ 0-100, grade A-F, projected score
 6 Summary plan .......... REFACTOR_PLAN.md + SECURE_CHECK_PLAN.txt
            |
            v   *** STOP - the AI waits for you ***
 You: "APPROVE RECOMMENDED"  /  "APPROVE FIX-01 SPAM-02"  /  "SKIP"
            |
            v
 7 Apply approved items .. new git branch/backup first; fixes -> config -> moves -> splits
                           -> quarantine (never hard-delete)                -> CHANGES_LOG.md
 8 Anti-spam ............. only the SPAM-* items you approved
 9 Verify & report ....... build/tests, re-scan, score before -> after
```

## 3. Target architecture

Every project is measured against this model:

```
 [ CLIENT ]  website / web app / mobile / desktop UI        public, untrusted
     |  HTTPS - API calls only
     v
 [ BACKEND ]  business logic, formulas, prices, permission checks, validation, secrets
     |                               |
     v                               v
 [ DATABASE ]                   [ FILE STORAGE ]
 structured data only           images, video, PDF, uploads
 (+ file metadata)              private by default, signed URLs
 never file bytes               never business data
```

- **Backend**: everything that decides money, access or truth (formulas, totals, discounts,
  scores, role and ownership checks).
- **Database**: structured records that must be there every time the app is opened. It keeps
  a reference to each file (key, type, size, owner) - never the file itself.
- **File storage**: images, video, PDF and other binary files.

## 4. Installation

The skill is plain Markdown + optional Python scripts. Copy the whole `SECURE_CHECK` folder.

| AI tool | How to install |
|---------|----------------|
| **Claude Code** | Copy the folder to `~/.claude/skills/secure-check/` (all projects) or `<project>/.claude/skills/secure-check/` (one project). It is picked up automatically; you can also type `/secure-check`. |
| **Claude.ai / Claude Desktop** | Zip the folder (the zip must contain `SKILL.md` at its top level, inside the folder) and upload it in *Settings → Capabilities → Skills*. |
| **Claude API / Agent SDK** | Upload as a custom skill, or place it in the agent's skills directory. |
| **OpenAI Codex, Jules, Aider, OpenCode, Amp, Zed** | Put the folder in your project (e.g. `tools/SECURE_CHECK/`) and copy `adapters/AGENTS.md` to the project root as `AGENTS.md` (merge if one exists). Fix the path inside. |
| **Gemini CLI** | Same as above, but name the file `GEMINI.md`. |
| **Cursor** | Folder in the project + copy `adapters/cursor-rule.mdc` to `.cursor/rules/secure-check.mdc`. |
| **GitHub Copilot** | Folder in the project + copy `adapters/copilot-instructions.md` to `.github/copilot-instructions.md` (merge if it exists). |
| **Windsurf** | Folder in the project + copy `adapters/AGENTS.md` content to `.windsurf/rules/secure-check.md`. |
| **Cline / Roo Code** | Folder in the project + copy `adapters/AGENTS.md` content to `.clinerules/secure-check.md`. |
| **ChatGPT, Gemini web, DeepSeek, Grok, any chat AI** | Paste the prompt from `adapters/PROMPT.md`, then upload your project (zip) or paste the important files. For better results also upload the `references/` files for your stack. In ChatGPT you can put it in a Project's instructions or a custom GPT. |

## 5. Usage

### Start (read-only, nothing is changed)

```
Run SECURE_CHECK on this project.
Check the security of this website and tell me what should be frontend and backend.
Quick secure check (secrets and public files only).
```

### Approve the plan

After the AI writes `secure-check-report/SECURE_CHECK_PLAN.txt`, reply with one of:

```
APPROVE RECOMMENDED                 apply the "Recommended now" set
APPROVE ALL                         apply everything
APPROVE FIX-01 CFG-01 SPAM-02       apply only these items
APPROVE ALL EXCEPT DEL-03 SPLIT-02  everything except these
SKIP                                keep the report, change nothing
```

Natural language in any language also works ("đồng ý FIX-01 và SPAM-02").

### Item types

| Prefix | Meaning |
|--------|---------|
| `FIX-` | Security fix in code |
| `CFG-` | Configuration (`.gitignore`, headers, debug flags, CORS, env example) |
| `MOVE-` | Move a file or code to the right layer/folder |
| `SPLIT-` | Split a file into clearer parts (no behaviour change) |
| `DEL-` | Move unused/junk files to `_quarantine/` (you delete them yourself) |
| `SPAM-` | Email/phone/form/OTP anti-spam protection |
| `YOU-` | Things only you can do (rotate a leaked key, DNS, cloud console) |

### Markers in the plan file

| Marker | Meaning |
|--------|---------|
| `!!!` | CRITICAL - real risk now, read first |
| `!!` | HIGH - fix soon |
| `!` | MEDIUM - needs attention |
| `(i)` | Info / good to know |
| `[?]` | Your decision is needed |
| `[YOU]` | Only you can do this |
| `[DEL]` | Proposed removal (to quarantine) |
| `>>>` | Start here |

Critical items and the score are inside `####` boxes so they cannot be missed.

## 6. Output files

```
secure-check-report/
  SECURE_CHECK_PLAN.txt   short highlighted plan - read this first
  SECURITY_REPORT.md      every finding: location, impact, fix
  FILE_MAP.md             every file: label, reason, proposed action
  REFACTOR_PLAN.md        proposed structure, moves, splits
  CHANGES_LOG.md          after APPLY: what changed and how to undo
  raw/                    scanner output (JSON) and preliminary score
_quarantine/              after APPLY: files set aside for you to delete
```

> `secure-check-report/` describes your vulnerabilities. **Never deploy or publish it.**

### Generated files stay on your machine (local-only)

Everything SECURE_CHECK generates - `secure-check-report/` (plan, reports, `CHANGES_LOG.md`,
`raw/`), `_quarantine/` and backup copies - is **never committed or pushed to git**:

- Each folder gets its own `.gitignore` containing `*`, so git ignores the whole folder
  (including that file). Your project's `.gitignore` is not touched.
- In a git repo, the folders are also added to `.git/info/exclude` (local to your clone,
  never committed).
- The AI never stages these files, even when you ask it to commit or push the project.
  Quarantined files are moved with a normal move, not `git mv`, so they stay untracked.
- Backup copies are created outside the project folder. The `secure-check/<date>` branch is
  never pushed by the AI.
- If an older run was already committed, the plan warns you and proposes
  `git rm -r --cached secure-check-report _quarantine` (files stay on disk).
- `templates/ci/pre-commit-hook.sh` also blocks any commit that contains these folders.

## 7. Security score

| Category | Weight |
|----------|--------|
| Secrets & credentials | 20 |
| Authentication & authorization | 20 |
| Input handling & injection | 15 |
| Public exposure | 10 |
| Database & file storage | 10 |
| Configuration & transport | 10 |
| Abuse & spam protection | 10 |
| Dependencies | 5 |

Each open finding deducts points inside its category: Critical 20, High 10, Medium 4, Low 1.
The score is capped at **49** while any Critical issue is open and at **79** while any High
issue is open. Grades: **A** 90+, **B** 75-89, **C** 60-74, **D** 40-59, **F** below 40.
Full rules: `references/scoring-rubric.md`.

## 8. Helper scripts (optional, for developers)

Python 3.8+, **standard library only** (no `pip install`), no network access. They only read
the project and write into `secure-check-report/raw/` (plus the local-only `.gitignore` and
`.git/info/exclude` entries).

```bash
# everything (inventory, secrets, exposure, contacts, code risks, split candidates, score)
python SECURE_CHECK/scripts/run_all.py path/to/project

# fast check for CI - exit code 1 if a critical lead is found
python SECURE_CHECK/scripts/run_all.py . --quick --fail-on critical

# individual scanners
python SECURE_CHECK/scripts/inventory.py .
python SECURE_CHECK/scripts/scan_secrets.py .            # values always masked
python SECURE_CHECK/scripts/scan_exposure.py .
python SECURE_CHECK/scripts/scan_contacts.py .
python SECURE_CHECK/scripts/scan_code_risks.py .
python SECURE_CHECK/scripts/find_split_candidates.py .
python SECURE_CHECK/scripts/score.py secure-check-report/raw/findings.json
```

Script hits are **leads**. The AI (or you) must confirm each one by reading the code; the
final score uses verified findings only.

**CI and git hooks:** `templates/ci/github-actions-secure-check.yml` (GitHub Actions) and
`templates/ci/pre-commit-hook.sh` (blocks commits that contain secrets or SECURE_CHECK's
generated files).

## 9. Safety guarantees

- Read-only until you approve. Approval is per item ID.
- A git branch (or a backup copy) is created before the first change.
- Nothing is permanently deleted - files go to `_quarantine/`.
- Secrets are always masked (`sk_l****9xQa`).
- No code or secrets are sent to outside services. No attacks on live sites, no deploys,
  no pushes.
- Everything the skill generates (reports, plan, quarantine, backups) stays local - it is
  never committed or pushed.
- Restructuring and splitting do not change how the app behaves.
- Honest reporting: skipped checks and failed builds/tests are reported as such.

## 10. Folder structure

```
SECURE_CHECK/
├── SKILL.md                 entry point for the AI
├── README.md                this file
├── adapters/                AGENTS.md, PROMPT.md, cursor-rule.mdc, copilot-instructions.md
├── workflow/                01-09: the step-by-step process
├── references/              rules, checklists, architecture, scoring, anti-spam, headers
│   └── stacks/              notes for 22 stacks (React, Next.js, Laravel, Django, Flutter ...)
├── templates/               report templates, .env.example, .gitignore, CI files
└── scripts/                 optional Python scanners (stdlib only)
```

## 11. Limitations

- SECURE_CHECK reviews **source code and configuration**. It is not a penetration test and
  does not test your live servers.
- Scanners use patterns; they can miss things and produce false positives. The AI's manual
  review is what counts, and AIs can also make mistakes - review the plan before approving.
- Hosting, DNS, cloud-console and key-rotation tasks must be done by you (`[YOU]` items).

---

# Tiếng Việt

## 1. SECURE_CHECK làm được gì

Khi bạn chạy SECURE_CHECK trên một dự án, AI sẽ:

1. **Đọc và lập bản đồ toàn bộ dự án**: loại dự án (website, web app, API, app mobile, app
   desktop, full-stack), công nghệ, điểm khởi chạy, nơi deploy.
2. **Phân loại từng file**: Frontend, Backend, Database, File storage, Dùng chung, Cấu hình,
   Riêng tư (không bao giờ được public), File tự sinh, Tài liệu, Test. AI cũng đánh dấu các
   vấn đề như key bí mật nằm ở frontend, logic nghiệp vụ chạy trên trình duyệt, file nên gỡ bỏ.
3. **Kiểm tra bảo mật**: lộ key/mật khẩu, file không được public, phân quyền, injection
   (SQL, XSS, command, SSRF...), đăng nhập, upload và lưu trữ file, cấu hình, giới hạn tần
   suất (rate limit), thư viện phụ thuộc, các vấn đề riêng của mobile/desktop.
4. **Chấm điểm bảo mật** từ 0 đến 100 kèm xếp loại (A-F), điểm từng hạng mục, và điểm dự kiến
   sau khi sửa.
5. **Đề xuất cấu trúc gọn gàng** và **tách code rối** thành các module rõ ràng, mỗi phần một
   nhiệm vụ, giúp phát triển dễ hơn về sau. Không có giới hạn số dòng cố định: tách theo
   trách nhiệm, tùy theo code của từng dự án.
6. **Bảo vệ email và số điện thoại** hiển thị trên web/app khỏi bot thu thập để spam, đồng
   thời bảo vệ form và OTP/SMS khỏi bị lạm dụng.
7. Viết **bản kế hoạch tóm gọn có đánh dấu nổi bật** (`SECURE_CHECK_PLAN.txt`) rồi **chờ bạn
   duyệt**. Không có gì bị thay đổi cho đến khi bạn đồng ý từng mục cụ thể.

## 2. Cách thức hoạt động

```
 Bạn: "Chạy SECURE_CHECK cho dự án này"
            |
            v
 1 An toàn & chế độ ...... mặc định chỉ đọc, kiểm tra git/bản sao lưu
 2 Khám phá .............. công nghệ, điểm khởi chạy, thư mục deploy, tình trạng kiến trúc
 3 Phân loại ............. mỗi file -> nhãn + cờ + lý do            -> FILE_MAP.md
 4 Kiểm tra bảo mật ...... checklist + script quét, có xác minh     -> SECURITY_REPORT.md
 5 Chấm điểm ............. 0-100, hạng A-F, điểm dự kiến sau khi sửa
 6 Kế hoạch tóm gọn ...... REFACTOR_PLAN.md + SECURE_CHECK_PLAN.txt
            |
            v   *** DỪNG - AI chờ bạn quyết định ***
 Bạn: "APPROVE RECOMMENDED"  /  "đồng ý FIX-01 SPAM-02"  /  "SKIP"
            |
            v
 7 Thực hiện mục đã duyệt  tạo nhánh git/bản sao lưu trước; sửa lỗi -> cấu hình -> di chuyển
                           -> tách code -> cách ly file (không xóa vĩnh viễn)  -> CHANGES_LOG.md
 8 Chống spam ............ chỉ các mục SPAM-* bạn đã đồng ý
 9 Kiểm tra & báo cáo .... build/test, quét lại, điểm trước -> sau
```

## 3. Kiến trúc chuẩn

Mọi dự án được đối chiếu với mô hình này:

```
 [ CLIENT ]  website / web app / app mobile / app desktop    công khai, không tin cậy
     |  HTTPS - chỉ gọi API
     v
 [ BACKEND ]  logic nghiệp vụ, công thức, giá, kiểm tra phân quyền, kiểm tra dữ liệu, bí mật
     |                               |
     v                               v
 [ DATABASE ]                   [ FILE STORAGE ]
 chỉ dữ liệu có cấu trúc        ảnh, video, PDF, file upload
 (+ thông tin mô tả file)       mặc định riêng tư, link có thời hạn
 không lưu nội dung file        không lưu dữ liệu nghiệp vụ
```

- **Backend**: mọi thứ quyết định tiền, quyền truy cập hoặc tính đúng đắn (công thức, tổng
  tiền, giảm giá, điểm số, kiểm tra vai trò và quyền sở hữu).
- **Database**: dữ liệu có cấu trúc, mỗi lần mở app đều phải có ở đó. Database chỉ lưu thông
  tin tham chiếu tới file (mã file, loại, dung lượng, chủ sở hữu), không lưu bản thân file.
- **File storage**: ảnh, video, PDF và các file nhị phân khác.

## 4. Cài đặt

Bộ skill là Markdown thuần + script Python tùy chọn. Hãy sao chép nguyên thư mục `SECURE_CHECK`.

| Công cụ AI | Cách cài |
|------------|----------|
| **Claude Code** | Chép thư mục vào `~/.claude/skills/secure-check/` (dùng cho mọi dự án) hoặc `<dự án>/.claude/skills/secure-check/` (một dự án). Skill được nhận tự động; cũng có thể gõ `/secure-check`. |
| **Claude.ai / Claude Desktop** | Nén thư mục thành file zip (bên trong thư mục phải có `SKILL.md`), tải lên ở *Settings → Capabilities → Skills*. |
| **Claude API / Agent SDK** | Tải lên dưới dạng custom skill, hoặc đặt vào thư mục skills của agent. |
| **OpenAI Codex, Jules, Aider, OpenCode, Amp, Zed** | Đặt thư mục vào dự án (vd: `tools/SECURE_CHECK/`), chép `adapters/AGENTS.md` ra thư mục gốc dự án thành `AGENTS.md` (nếu đã có thì gộp nội dung). Sửa lại đường dẫn bên trong. |
| **Gemini CLI** | Như trên, nhưng đặt tên file là `GEMINI.md`. |
| **Cursor** | Thư mục trong dự án + chép `adapters/cursor-rule.mdc` vào `.cursor/rules/secure-check.mdc`. |
| **GitHub Copilot** | Thư mục trong dự án + chép `adapters/copilot-instructions.md` vào `.github/copilot-instructions.md` (gộp nếu đã có). |
| **Windsurf** | Thư mục trong dự án + chép nội dung `adapters/AGENTS.md` vào `.windsurf/rules/secure-check.md`. |
| **Cline / Roo Code** | Thư mục trong dự án + chép nội dung `adapters/AGENTS.md` vào `.clinerules/secure-check.md`. |
| **ChatGPT, Gemini bản web, DeepSeek, Grok, AI chat bất kỳ** | Dán prompt trong `adapters/PROMPT.md`, sau đó tải dự án lên (file zip) hoặc dán các file quan trọng. Để kết quả tốt hơn, tải thêm các file `references/` đúng công nghệ của bạn. Với ChatGPT có thể đưa vào phần hướng dẫn của Project hoặc custom GPT. |

## 5. Cách sử dụng

### Bắt đầu (chỉ đọc, không thay đổi gì)

```
Chạy SECURE_CHECK cho dự án này.
Kiểm tra bảo mật website này và cho mình biết cái nào là frontend, cái nào là backend.
Quick secure check (chỉ kiểm tra key bị lộ và file public).
```

### Duyệt kế hoạch

Sau khi AI tạo file `secure-check-report/SECURE_CHECK_PLAN.txt`, bạn trả lời một trong các cách:

```
APPROVE RECOMMENDED                 làm các mục "Recommended now" (đề xuất làm ngay)
APPROVE ALL                         làm tất cả
APPROVE FIX-01 CFG-01 SPAM-02       chỉ làm các mục này
APPROVE ALL EXCEPT DEL-03 SPLIT-02  làm tất cả trừ các mục này
SKIP                                giữ báo cáo, không thay đổi gì
```

Viết tự nhiên bằng tiếng Việt cũng được: "đồng ý FIX-01 và SPAM-02".

### Các loại mục

| Tiền tố | Ý nghĩa |
|---------|---------|
| `FIX-` | Sửa lỗi bảo mật trong code |
| `CFG-` | Cấu hình (`.gitignore`, header, chế độ debug, CORS, file env mẫu) |
| `MOVE-` | Di chuyển file/code về đúng tầng, đúng thư mục |
| `SPLIT-` | Tách file thành các phần rõ ràng hơn (không đổi chức năng) |
| `DEL-` | Chuyển file thừa/rác vào `_quarantine/` (bạn tự xóa sau) |
| `SPAM-` | Chống spam cho email/số điện thoại/form/OTP |
| `YOU-` | Việc chỉ bạn làm được (đổi key bị lộ, DNS, trang quản trị cloud) |

### Ký hiệu trong file kế hoạch

| Ký hiệu | Ý nghĩa |
|---------|---------|
| `!!!` | NGHIÊM TRỌNG - rủi ro thật ngay lúc này, đọc đầu tiên |
| `!!` | CAO - cần sửa sớm |
| `!` | TRUNG BÌNH - cần lưu ý |
| `(i)` | Thông tin / nên biết |
| `[?]` | Cần bạn quyết định |
| `[YOU]` | Chỉ bạn làm được |
| `[DEL]` | Đề xuất gỡ bỏ (chuyển vào khu cách ly) |
| `>>>` | Bắt đầu đọc từ đây |

Điểm số và các lỗi nghiêm trọng được đóng khung `####` để bạn không thể bỏ sót.

## 6. Các file kết quả

```
secure-check-report/
  SECURE_CHECK_PLAN.txt   kế hoạch tóm gọn có đánh dấu - đọc file này trước
  SECURITY_REPORT.md      chi tiết từng lỗi: vị trí, tác hại, cách sửa
  FILE_MAP.md             từng file: nhãn, lý do, hành động đề xuất
  REFACTOR_PLAN.md        cấu trúc đề xuất, bảng di chuyển, kế hoạch tách code
  CHANGES_LOG.md          sau khi thực hiện: đã đổi gì và cách hoàn tác
  raw/                    kết quả script quét (JSON) và điểm sơ bộ
_quarantine/              sau khi thực hiện: file được cách ly chờ bạn xóa
```

> Thư mục `secure-check-report/` mô tả các lỗ hổng của bạn. **Không bao giờ deploy hay public thư mục này.**

### File do skill sinh ra chỉ giữ trên máy bạn (local-only)

Mọi thứ SECURE_CHECK sinh ra - `secure-check-report/` (kế hoạch, báo cáo, `CHANGES_LOG.md`,
`raw/`), `_quarantine/` và bản sao lưu - **không bao giờ được commit hay push lên git**:

- Mỗi thư mục có một file `.gitignore` riêng chứa `*`, nên git bỏ qua toàn bộ thư mục (kể cả
  chính file đó). File `.gitignore` của dự án không bị đụng tới.
- Trong repo git, các thư mục này còn được thêm vào `.git/info/exclude` (chỉ có ở máy bạn,
  không bao giờ được commit).
- AI không bao giờ `git add` các file này, kể cả khi bạn yêu cầu commit hoặc push dự án.
  File cách ly được chuyển bằng lệnh di chuyển thường, không dùng `git mv`, nên không bị git theo dõi.
- Bản sao lưu được tạo bên ngoài thư mục dự án. Nhánh `secure-check/<ngày>` không bao giờ
  được AI push.
- Nếu lần chạy trước đã lỡ commit báo cáo, kế hoạch sẽ cảnh báo và đề xuất
  `git rm -r --cached secure-check-report _quarantine` (file vẫn giữ trên máy).
- `templates/ci/pre-commit-hook.sh` cũng chặn mọi commit có chứa các thư mục này.

## 7. Chấm điểm bảo mật

| Hạng mục | Trọng số |
|----------|----------|
| Bí mật & thông tin đăng nhập | 20 |
| Xác thực & phân quyền | 20 |
| Xử lý dữ liệu đầu vào & injection | 15 |
| Lộ file ra public | 10 |
| Database & lưu trữ file | 10 |
| Cấu hình & truyền tải | 10 |
| Chống lạm dụng & spam | 10 |
| Thư viện phụ thuộc | 5 |

Mỗi lỗi chưa sửa bị trừ điểm trong hạng mục của nó: Nghiêm trọng 20, Cao 10, Trung bình 4,
Thấp 1. Điểm tối đa bị giới hạn ở **49** khi còn lỗi Nghiêm trọng và ở **79** khi còn lỗi
Cao. Xếp loại: **A** từ 90, **B** 75-89, **C** 60-74, **D** 40-59, **F** dưới 40.
Quy tắc đầy đủ: `references/scoring-rubric.md`.

## 8. Script hỗ trợ (tùy chọn, cho lập trình viên)

Python 3.8+, **chỉ dùng thư viện chuẩn** (không cần `pip install`), không kết nối mạng.
Script chỉ đọc dự án và ghi kết quả vào `secure-check-report/raw/` (kèm file `.gitignore`
local-only và dòng trong `.git/info/exclude`).

```bash
# chạy tất cả (kiểm kê, secret, file public, liên hệ, code rủi ro, gợi ý tách file, điểm)
python SECURE_CHECK/scripts/run_all.py duong/dan/du-an

# kiểm tra nhanh cho CI - trả mã lỗi 1 nếu phát hiện vấn đề nghiêm trọng
python SECURE_CHECK/scripts/run_all.py . --quick --fail-on critical

# từng script riêng
python SECURE_CHECK/scripts/inventory.py .
python SECURE_CHECK/scripts/scan_secrets.py .            # giá trị luôn được che
python SECURE_CHECK/scripts/scan_exposure.py .
python SECURE_CHECK/scripts/scan_contacts.py .
python SECURE_CHECK/scripts/scan_code_risks.py .
python SECURE_CHECK/scripts/find_split_candidates.py .
python SECURE_CHECK/scripts/score.py secure-check-report/raw/findings.json
```

Kết quả của script chỉ là **gợi ý**. AI (hoặc bạn) phải đọc code để xác nhận từng gợi ý;
điểm cuối cùng chỉ tính các lỗi đã được xác minh.

**CI và git hook:** `templates/ci/github-actions-secure-check.yml` (GitHub Actions) và
`templates/ci/pre-commit-hook.sh` (chặn commit có chứa secret hoặc file do SECURE_CHECK sinh ra).

## 9. Cam kết an toàn

- Chỉ đọc cho đến khi bạn duyệt. Duyệt theo từng mã mục.
- Tạo nhánh git (hoặc bản sao lưu) trước thay đổi đầu tiên.
- Không xóa vĩnh viễn file nào - file được chuyển vào `_quarantine/`.
- Secret luôn được che (`sk_l****9xQa`).
- Không gửi code hay secret ra dịch vụ bên ngoài. Không tấn công thử web đang chạy, không
  deploy, không push.
- Mọi file skill sinh ra (báo cáo, kế hoạch, khu cách ly, bản sao lưu) chỉ giữ ở máy bạn -
  không bao giờ được commit hay push lên git.
- Sắp xếp lại và tách code không làm thay đổi cách app hoạt động.
- Báo cáo trung thực: kiểm tra nào bị bỏ qua, build/test nào lỗi đều được ghi rõ.

## 10. Cấu trúc thư mục

```
SECURE_CHECK/
├── SKILL.md                 điểm vào cho AI
├── README.md                file này
├── adapters/                AGENTS.md, PROMPT.md, cursor-rule.mdc, copilot-instructions.md
├── workflow/                01-09: quy trình từng bước
├── references/              luật, checklist, kiến trúc, chấm điểm, chống spam, header
│   └── stacks/              ghi chú cho 22 công nghệ (React, Next.js, Laravel, Django, Flutter ...)
├── templates/               mẫu báo cáo, .env.example, .gitignore, file CI
└── scripts/                 script quét Python tùy chọn (thư viện chuẩn)
```

## 11. Giới hạn

- SECURE_CHECK kiểm tra **mã nguồn và cấu hình**. Đây không phải kiểm thử xâm nhập
  (pentest) và không tấn công thử server đang chạy của bạn.
- Script quét dựa trên mẫu nhận diện nên có thể bỏ sót hoặc báo nhầm. Kết quả xem xét thủ
  công của AI mới là chính, và AI cũng có thể sai, nên hãy đọc kỹ kế hoạch trước khi duyệt.
- Các việc về hosting, DNS, trang quản trị cloud và đổi key phải do bạn tự làm (mục `[YOU]`).
