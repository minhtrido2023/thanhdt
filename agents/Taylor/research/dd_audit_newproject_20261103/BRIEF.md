# Brief rà soát DD theo luật "đầu tư dự án mới" (user 03/11/2026)
Đọc: ~/.claude/skills/due-diligence/SKILL.md dòng 31 (luật), dd-investor-report luật 20.
Luật: case base: dự án đang/sắp đầu tư = GIÁ SỔ SÁCH/CHI PHÍ (NPV=0); phần đã chi là tài sản theo giá vốn (không vừa trong nợ vừa bị coi mất); chỉ lệch khi có CƠ SỞ ĐỘC LẬP CỤ THỂ có nguồn. (+) cần cơ sở giá/sản lượng/hợp đồng; (−) cần rủi ro cụ thể quan sát được -> kịch bản có xác suất, không nhét vào base. Cấm: đường giá "nguồn cung chính dự án làm sập giá" ở base; chi phí vốn cao hơn vay/hợp đồng thực tế khiến NPV âm mặc định.
CHỈ RÀ. KHÔNG sửa file gốc, không gửi email, không dựng lại báo cáo. Nếu chạy lại mô hình: COPY calc sang /home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_audit_newproject_20261103/calc/<TICKER>/ rồi chạy bản copy (PYTHONHASHSEED=0, system python3 hoặc /home/trido/thanhdt/wc_venv/bin/python), đổi tham số để dự án = sổ sách/NPV 0 và so với tâm gốc. Không chạy được -> ước từ số trong báo cáo, GHI RÕ "ước lượng".
Sổ hiện hành: kb/dd_price_zones.json (lấy entry dd_date MỚI NHẤT của mã; tâm/vùng/source_file). Giá đóng cửa 03/11: agents/Taylor/research/dd_audit_newproject_20261103/close_20261103.md.
Mỗi mã, viết file agents/Taylor/research/dd_audit_newproject_20261103/parts/<TICKER>.md, ĐÚNG khung:
1. Tâm/vùng hiện hành + đường dẫn báo cáo nguồn (và REPORT.md gốc nếu khác)
2. Dự án mới/cam kết vốn/mở rộng/M&A trong báo cáo (tên, vốn, tiến độ) — hoặc "không có", kèm file:dòng bằng chứng (grep từ khoá: dự án, đầu tư, capex, mở rộng, nhà máy, mỏ, M&A, NPV, IRR, WACC, Ke, vách giá, cung mới)
3. Mô hình có TRỪ giá trị ở base vì dự án đó không (cơ chế cụ thể + file:dòng) và CÓ cơ sở độc lập nêu nguồn không; có khoản CỘNG không cơ sở không
4. Phân loại: KHÔNG_VẤN_ĐỀ / NHẸ(<5% tâm) / ĐÁNG_KỂ(5–15%) / NGHIÊM_TRỌNG(>15%) / KHÔNG_ĐÁNH_GIÁ_ĐƯỢC(thiếu gì)
5. Hiệu ứng lên tâm khi đặt dự án ở sổ sách/NPV 0: đ/cp và %, ghi "đã chạy lại <file>" hoặc "ước lượng: <cách tính>"
6. (Ghi RIÊNG sau cùng) giá 03/11 vs tâm gốc vs tâm điều chỉnh: nhãn có đổi qua ngưỡng ứng viên (giá ≤ tâm×0,85) không, và vùng rẻ/đắt nếu báo cáo có thang.
Số nào cũng phải đọc/đo trong phiên, không bịa. Cuối phiên trả lời: bảng 1 dòng/mã (mã | phân loại | hiệu ứng % | nhãn đổi?) + 1 câu nguyên nhân chính. Ngắn gọn.
