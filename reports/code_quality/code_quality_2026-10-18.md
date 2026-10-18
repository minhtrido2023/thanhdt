# Code quality weekly — 2026-10-18

File đã quét: 25 (nguồn FALLBACK diff 7 ngày (manifest HEAD lệch thực tế (production_manifest.py --check): DRIFT 3 dòng — manifest commit lệch thực tế. Nếu thay đổi là CỐ Ý: chạy `python3 mike/bin/production_manifest.py` rồi commit kb/production_manifest.{json,md}. + mike/bin/finding_measured_by.py [T0] (mới vào production, từ mike/bin/append_event.sh) + mike/bin/gate_source_check.py [T0] (mới vào production, từ mike/bin/bq_freshness_check.sh)); hot-core round-robin: /home/trido/thanhdt/WorkingClaude/mike/bin/ops_health_check.sh)
Finding: 14 (từ 14 trước verify)

## mike/bin/ops_health_check.sh:2047 — correctness (high)
- Owner đề xuất: Wags
- Nếu heredoc python crash (exception ngoài try) thì checker FAIL-OPEN: REPORT rỗng, WARN_COUNT rỗng bị coi là 0 ⇒ post 'mọi khâu vận hành bình thường' với thân báo cáo trống và không dispatch autofix.
- Bằng chứng: L2047: WARN_COUNT="$(echo "$REPORT" | grep -o '__WARN_COUNT__=[0-9]*' | cut -d= -f2)"; L2058: WARN_COUNT=$(( ${WARN_COUNT:-0} + ... )); L2165: if [ "${WARN_COUNT:-0}" -eq 0 ]; then ... '**Kết luận: mọi khâu vận hành bình thường, không cần can thiệp.**'. Không có nhánh nào xử lý trường hợp thiếu marker __WARN_COUNT__ (grep WARN_COUNT chỉ ra các dòng 2043/2047/2058/2100/2126/2165/2208/2216). Trong heredoc có đường không bọc try: check 3 đọc journal bằng csv.DictReader (L184-196, file có byte NUL ⇒ _csv.Error), check 2 so `if pd < today` (L159, plan_date không phải str ⇒ TypeError). ops_health_check_selfcheck.py không có ca nào cho heredoc crash (grep '__WARN_COUNT__' chỉ thấy L2565 dùng để trích khối).
- Hướng sửa đề xuất: Sau L2047: nếu REPORT không chứa marker __WARN_COUNT__ thì đặt WARN_COUNT=1 và thêm một dòng ⚠️ 'ops_health_check: khối python chết giữa chừng — báo cáo KHÔNG đầy đủ' (bắt stderr của heredoc vào file tạm rồi in đuôi), để dòng đó rơi vào OTHER_WARN. Thêm 1 ca selfcheck: heredoc raise ⇒ không được ra kết luận 'bình thường'.
- Đã qua verify độc lập: sống sót phản biện.

## mike/bin/ops_health_check.sh:1481 — correctness (medium)
- Owner đề xuất: Wags
- Thông điệp WARN của check 8b vẫn nói CCTG stale/lỗi thì 'rơi về Big-4-only (hành vi ĐỔI THẬT)'. Từ 13-14/10 deposit_rate_vn giữ CCTG gần nhất đã biết (cctg_held), nên thông điệp chẩn đoán đã sai sự thật (§29).
- Bằng chứng: ops_health_check.sh L1481: '...effective_deposit_rate() tự coi CCTG là stale và rơi về Big-4-only (hành vi ĐỔI THẬT, không chỉ cảnh báo)'; L1444: '5 consumer LIVE đang âm thầm rơi về Big-4-only'. deposit_rate_vn.py L390-395/L403-411: stale/unavailable ⇒ rate_source='cctg_held(...)', '_log.warning(... HOLDING last known CCTG ..., not dropping to Big-4)'. git log deposit_rate_vn.py: 0b29d2d1e 'giữ CCTG gần nhất đã biết khi stale/lỗi, không tụt về Big-4 (user duyệt 13/10)', 024f4a15f (14/10).
- Hướng sửa đề xuất: Sửa câu chữ ở L1444/L1481 (và comment L1399/L1411) theo hành vi hiện tại: quá ngày thứ 45 thì số được GIỮ ở mức CCTG cũ và gắn nhãn cctg_held kèm WARNING, không tụt về Big-4. Mục đích là để người đọc đánh giá đúng mức khẩn.
- Đã qua verify độc lập: sống sót phản biện.

## deploy_golive_dt5g_v4/golive_recommend_v23.py:452 — bare-datetime-now (medium)
- Owner đề xuất: Taylor
- Tuổi active_nav tính bằng pd.Timestamp.now() không neo TZ, trong khi cả file đều dùng _ICT. Chạy dưới TZ host khác ICT trong khung 00:00-07:00 ICT thì active_nav vừa ghi hôm nay có tuổi -1 ⇒ bị coi là QUÁ HẠN ⇒ slot target CAPIT/%ADV rơi về nav_history TỔNG NAV (chưa trừ excluded_tickers).
- Bằng chứng: L452: age = (pd.Timestamp.now().normalize() - pd.Timestamp(d["computed_at"])).days; L453: if 0 <= age <= ACTIVE_NAV_MAX_AGE_D ... ; computed_at là ngày trần (data/execution_logs/active_nav_SpaceX.json: "computed_at": "2026-10-16"). Cùng file L89-91, L1336 đều dùng datetime.now(_ICT). pd.Timestamp.now() nằm NGOÀI phạm vi tz_anchor_gate (coding_guidelines §16: 'CHƯA phủ: pd.Timestamp.now()').
- Hướng sửa đề xuất: Thay bằng pd.Timestamp.now(tz="Asia/Ho_Chi_Minh").normalize().tz_localize(None), cùng mẫu với deposit_rate_vn.current_deposit_rate.
- Đã qua verify độc lập: sống sót phản biện.

## dcf_valuation.py:493 — duplicate-formula (medium)
- Owner đề xuất: Taylor
- Công thức DCF status/robust (CHEAP⇔MoS>0, robust = dấu MoS giữ nguyên qua 4 điểm sensitivity) bị chép tay ở 4 nơi. Một nơi đổi (thêm key sensitivity, đổi điều kiện px>0) thì các nơi còn lại lệch im lặng.
- Bằng chứng: dcf_valuation.py L493-505 (dcf_check, _SENS_KEYS L466); trading_bot/strategies.py L74-88 (_dcf_check_for_order, _DCF_SENS_KEYS L24); custom_basket.py L889-917 (dcf_at, tuple key viết cứng L908); dcf_selector_selfcheck.py L54-73 (status_live). grep '"r-1%", "r+1%", "g-2%", "g+2%"\|_SENS_KEYS' ra cả 4 file. Các bản đã khác nhau nhỏ: strategies đòi `price and price > 0`, custom_basket đòi `px and px > 0` trước fair_value, dcf_check đòi `px > 0` sau.
- Hướng sửa đề xuất: Tách 1 hàm thuần trong dcf_valuation.py (vd classify_dcf(res, px) -> (status, mos, robust)) rồi cho strategies._dcf_check_for_order, dcf_check và custom_basket.dcf_at cùng gọi. Selfcheck test chính hàm đó.
- Đã qua verify độc lập: sống sót phản biện.

## dcf_selector_selfcheck.py:92 — correctness (medium)
- Owner đề xuất: Taylor
- Check [1] so bản CHÉP RIÊNG status_live() của selfcheck với production, chứ không so custom_basket.dcf_at (code thật đang được kiểm). Nếu dcf_at lệch khỏi production thì selfcheck vẫn xanh. Check [2] cũng chép lại 'verbatim logic' thay vì gọi code thật.
- Bằng chứng: L54-73 định nghĩa status_live (chép logic); L92: mine = status_live(r.ticker, r.d, float(r.Price)); L93: prod = _dcf_check_for_order(...). custom_basket.dcf_at (custom_basket.py L889) là closure trong build_pit, selfcheck không gọi tới nó. L115-116: '# variant A path (verbatim logic from custom_basket.py)' rồi tự viết lại biểu thức lambda. Docstring L49 nói 'the cache parquet is no longer a dependency' nhưng L87/L137 vẫn đọc CACHE parquet.
- Hướng sửa đề xuất: Kiểm đúng đối tượng: hoặc dùng hàm phân loại chung (xem finding duplicate-formula), hoặc trích dcf_at theo marker như capit_lever_selfcheck (extract-and-exec) để [1] chạy trên code thật của custom_basket.
- Đã qua verify độc lập: sống sót phản biện.

## basket_price_basis_audit_selfcheck.py:71 — assert-on-live-state (medium)
- Owner đề xuất: Taylor
- NEGATIVE control assert 'Close==Price cho MỌI mã' trên rổ 30 mã chép cứng (rebal 2026-05-05), đọc bar mới nhất LIVE không có asof. Chỉ cần 1 mã ngừng giao dịch/treo là sweep đỏ — đúng failure mode đã cắn leg STALE ngày 2026-10-16, nhưng mới vá cho STALE.
- Bằng chứng: L47-49 BASKET = ['ACB', ... 'VRE'] ('The live basket (2026-05-05 rebal ...)'); L71: b = last_bar(BASKET)  # asof=None; L75-77: check('NEGATIVE: current basket weights identical on both bases', gap_basket < 1e-12, ...). So với L54-57: 'Read "latest bar" live, names that later resume trading ... silently drop out of the control (2026-10-16 ... sweep RED)' ⇒ STALE_ASOF = "2026-08-02" chỉ áp cho STALE (L79).
- Hướng sửa đề xuất: Ghim leg BASKET vào asof cố định (vd last_bar(BASKET, asof="2026-08-02"), ngày fixture được tuyển), giống STALE_ASOF, để assert lên fixture đã đóng băng chứ không lên trạng thái giao dịch hôm nay (§23 hệ luận 1).
- Đã qua verify độc lập: sống sót phản biện.

## mike/bin/ops_health_check.sh:1588 — correctness (low)
- Owner đề xuất: Wags
- Check 9b dựng tập câu hỏi còn mở bằng matcher riêng, lệch hẳn check #5: (a) quét thư mục không tồn tại `mike/bus/archive/*.jsonl` thay vì archive thật `bus/inbox/archive/*.jsonl.gz`; (b) đi 1 lượt theo thứ tự file, nên answer nằm ở file agent sort trước sẽ bị xử lý trước câu hỏi ⇒ câu hỏi đã trả lời vẫn được tính là backing.
- Bằng chứng: L1588-1589: for _bd in [.../bus/inbox, .../bus/archive]; L1593: if not _fn9b.endswith(".jsonl"): continue; ls mike/bus/ không có 'archive' (có inbox/archive/*.jsonl.gz, đúng như check #5 L476-478). L1597-1601: question ⇒ add, answer/decision ⇒ discard, cùng 1 vòng lặp theo sorted(listdir). Đây đúng lỗi chéo-agent mà check #5 đã sửa bằng 2 pass ('answers gom TOÀN CỤC trước', comment L330-333). Hiện latent: grep -c PENDING_DECISION mike/kb/memory/Mike.md = 0.
- Hướng sửa đề xuất: Cho 9b dùng lại kết quả matcher của check #5 (pending_q + aged_q, vốn đã quét archive .gz theo 2 pass), hoặc ít nhất đổi đường dẫn sang inbox/archive/*.jsonl.gz và gom resolver toàn cục trước khi duyệt question.

## mike/bin/ops_health_check.sh:2201 — bare-datetime-now (low)
- Owner đề xuất: Wags
- `date -Iseconds` không có tiền tố TZ='Asia/Ho_Chi_Minh' khi ghi vào notify_thread_errors.log; ngoài ra check 8 L1369 dùng `_date.fromtimestamp(mtime)` (giờ host) trừ cho today_d (ICT).
- Bằng chứng: L2201: "$(date -Iseconds)" "$TRADING_DAILY_THREAD" ... >> "$ROOT/logs/notify_thread_errors.log"; script không export TZ (L115-116 neo TZ từng lệnh riêng). L1369: dep_run_days = (today_d - _date.fromtimestamp(os.path.getmtime(dep_runs[-1]))).days. Hiện chỉ được che bởi dòng TZ=Asia/Ho_Chi_Minh trong crontab.
- Hướng sửa đề xuất: Đổi thành $(TZ='Asia/Ho_Chi_Minh' date -Iseconds), và _dt.datetime.fromtimestamp(mtime, ZoneInfo("Asia/Ho_Chi_Minh")).date() ở L1369.

## deploy_golive_dt5g_v4/publish_gated_state.py:38 — bare-datetime-now (low)
- Owner đề xuất: Taylor
- END (ngày cuối chuỗi state đem publish) và published_at dùng datetime.now() trần. Chạy dưới TZ host khác ICT trước 07:00 ICT thì END = hôm qua. File đang nằm trong nợ baseline của tz_anchor_gate (2 vi phạm).
- Bằng chứng: L38: END = datetime.now().strftime("%Y-%m-%d"); L104: "published_at": datetime.now().isoformat(timespec="seconds") (naive, được check 13 của ops_health_check và gate bq_freshness đọc). mike/kb/tz_anchor_baseline.json L16: "deploy_golive_dt5g_v4/publish_gated_state.py": 2.
- Hướng sửa đề xuất: Thêm _ICT = ZoneInfo("Asia/Ho_Chi_Minh") và dùng datetime.now(_ICT) ở cả 2 chỗ (cùng mẫu golive_recommend_v23.py L89), rồi hạ baseline bằng --update-baseline.

## deploy_golive_dt5g_v4/publish_gated_state.py:113 — guideline:§5 (low)
- Owner đề xuất: Taylor
- golive_state_today.json (file trạng thái dùng chung, ≥6 consumer đọc) được ghi đè trực tiếp, không qua tmp + os.replace. Bị kill giữa lúc ghi sẽ để lại JSON dở.
- Bằng chứng: L113: json.dump(prov, open(STATE_JSON, "w", encoding="utf-8"), indent=2). Consumer: golive_recommend_v23.py L643, mike/bin/gate_source_check.py, send_plan_report.sh, eod_trading_report.sh, ops_health_check.sh check 13 (L1962), bq_freshness gate publisher-evidence.
- Hướng sửa đề xuất: Ghi ra STATE_JSON + '.tmp' (hoặc tempfile.mkstemp cùng thư mục) rồi os.replace, đúng §5.

## deposit_cctg_trend_check.py:277 — guideline:§5 (low)
- Owner đề xuất: Taylor
- Cờ 'đã báo' chỉ được ghi xuống đĩa ở cuối vòng lặp (L317), và chỉ khi CẢ Discord lẫn bus thành công. Discord đã gửi mà append_event lỗi (hoặc bị kill trước L317) ⇒ lần chạy sau gửi LẠI Discord. Còn khi NOTIFY_OFF thì bus finding bị append lại mỗi lần chạy.
- Bằng chứng: L260: notify_status = _send_trading_daily(msg); L268-271: bus_rc = append_event.sh ...; L277-279: chỉ đánh dấu alerted_pair khi notify_status == "sent" and bus_rc == 0; L280-282: suppressed + bus_rc==0 ⇒ không đánh dấu, bus đã ghi; L316-317: _write_state_atomic(state) chạy 1 lần sau mọi vòng lặp.
- Hướng sửa đề xuất: Ghi trạng thái riêng cho từng kênh (discord_sent / bus_sent cho mỗi pair), lần sau chỉ gửi lại kênh còn thiếu, và gọi _write_state_atomic ngay sau mỗi lần gửi thành công thay vì gom cuối vòng.

## daily_refresh_v34b_linux.sh:101 — correctness (low)
- Owner đề xuất: Taylor
- Nhánh retry của step [3] xoá cache ở SAI đường dẫn (root) trong khi ew_v1 đọc/ghi `data/_cache_universe_2013_now.pkl`. 'clearing cache + retry' thực chất retry trên đúng cache cũ, nên lỗi do cache hỏng sẽ lặp lại cả 3 lần rồi die.
- Bằng chứng: L101: echo "  ew_v1 attempt $try failed; clearing cache + retry"; rm -f _cache_universe_2013_now.pkl; vnindex_5state_ew_v1.py L51: CACHE_TICKER = os.path.join(WORKDIR, "data/_cache_universe_2013_now.pkl"); step [1] L95 xoá đúng data/_cache_universe_2013_now.pkl. ls: root/_cache_universe_2013_now.pkl không tồn tại, data/... có (208MB).
- Hướng sửa đề xuất: Đổi L101 thành rm -f data/_cache_universe_2013_now.pkl (khớp step [1] và CACHE_TICKER).

## custom_basket.py:1330 — correctness (low)
- Owner đề xuất: Taylor
- route_asof() rơi về route SỚM NHẤT đã biết khi quý chọn còn trước toàn bộ lịch sử route, tức dùng thông tin tương lai (look-ahead). Hàm anh em roemin_asof() ngay dưới cố ý KHÔNG làm vậy vì đúng lý do này.
- Bằng chứng: L1330: return e[1][i] if i >= 0 else e[1][0]; L1339: return e[1][i] if i >= 0 else None   # deliberately NO earliest-known fallback (look-ahead). route_asof được is_fin() dùng (L1333) cho fincap/RISK_SCOPE=fin. Route ngành hiếm khi đổi nên ảnh hưởng số liệu nhỏ.
- Hướng sửa đề xuất: Trả None khi i < 0 cho nhất quán với roemin_asof (is_fin(None) ⇒ False), hoặc ghi rõ trong code vì sao route được miễn luật PIT.

## append_cctg_rate.py:341 — code-smell:Duplicated Code (low)
- Owner đề xuất: Taylor
- Khối kiểm --sources (parse JSON, owner-group, tuổi nguồn, rate từng nguồn, spread, --rate khớp nguồn) bị chép gần nguyên văn từ append_deposit_rate.py và đã lệch nhau. Docstring nói 'reuse ... by import rather than duplicating' nhưng chỉ import 3 helper, phần còn lại vẫn là bản chép.
- Bằng chứng: append_cctg_rate.py L341-395 vs append_deposit_rate.py L358-438. Đã lệch: rào rate nguồn (0.5,30) vs (0,30) (L384 vs L428); deposit cho phép người dùng bỏ rate (L417-421), cctg bắt buộc (L376-379). Docstring append_cctg_rate L22-25 còn ghi 'deliberately NOT retrofitted into append_deposit_rate.py', nhưng deposit đã có cross-check rate (L409-438).
- Hướng sửa đề xuất: Đưa phần kiểm --sources vào 1 hàm chung trong append_deposit_rate.py (nhận rate_min/max và cờ require_rate), để append_cctg_rate gọi lại. Sửa docstring L22-25 cho khớp thực tế.

## File đã đọc kỹ, không có vấn đề (16)
- cctg_deposit_asof_ict_selfcheck.py
- capit_lever_selfcheck.py
- cctg_deposit_wiring_selfcheck.py
- cctg_overlay_selfcheck.py
- cctg_rate_vn.py
- cctg_tier2_series_selfcheck.py
- cpi_vn_tier15_selfcheck.py
- custom30_yield_labels_selfcheck.py
- daily_refresh_morning_selfcheck.sh
- dcf_refresh_gate.py
- dcf_refresh_gate_selfcheck.py
- deposit_fallback_direction_selfcheck.py
- deposit_rate_vn.py
- dna_report.py
- dna_report_killswitch_line_selfcheck.py
- append_deposit_rate.py