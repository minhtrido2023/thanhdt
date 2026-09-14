# -*- coding: utf-8 -*-
"""oshares_selfcheck_fixture.py — feed BigQuery ĐÓNG BĂNG cho selfcheck `oshares_live` / `oshares_pit`.

VÌ SAO (2026-09-14, user duyệt 23:43 ICT, job Taylor_20260914_164512). `corp_action_daily.py`
chạy `oshares_live.py --selfcheck` làm CỔNG trước khi publish. Các check đọc BQ SỐNG biến "feed
hôm nay trông y hệt hôm nghiệm thu" thành điều kiện publish: một dòng AIS mới của KHP về BQ tối
14/09 đã làm K1/K1b đỏ ⇒ sáng hôm sau không publish. Luật không được rot theo feed (§23 hệ luận 1,
`mike/kb/coding_guidelines_ext.md`).

NGUỒN. Từng dòng dưới đây là dòng `oshares_live._fetch` trả về NGUYÊN VĂN ngày 2026-09-14 (chuỗi
như bq CLI trả — '5.47292E7', '0.0' — không đổi kiểu, không làm tròn). Mỗi mã chỉ giữ một CỬA SỔ
LIỀN NGÀY: trần = asof lớn nhất selfcheck hỏi mã đó; sàn corp rồi sàn quý = ngày MUỘN NHẤT mà mọi
lời gọi tầng ngoài của selfcheck (oshares_at / _ais_verdicts / oshares_pit / oshares_reconciled,
kể cả các lượt vá cổng N3/F1c/N4/A6/A11/A13) vẫn ra output TRÙNG KHÍT từng field với feed BQ đầy
đủ. Không cắt tỉa lẻ từng dòng. Bằng chứng + script tái lập:
`mike/agents/Taylor/research/oshares_freeze_live_20260914/` (capture.py → freeze.py → gen_fixture.py).

ĐỪNG sửa tay một con số ở đây để check xanh lại: fixture là dữ liệu vendor đã chụp, không phải kỳ
vọng. Cần ca mới ⇒ chụp lại bằng capture.py/freeze.py và ghi cửa sổ mới vào docstring này.
"""

FROZEN_AT = "2026-09-14"
Q_COLS = ("time", "OShares")
C_COLS = ('event_code', 'exright_date', 'effective_date', 'listing_date', 'exercise_ratio', 'issue_volumn', 'issue_method_name_vi', 'shares_delta', 'shares_total_after', 'title')

# mã: (trần asof, sàn corp, sàn quý, số dòng quý giữ/đầy đủ, số dòng corp giữ/đầy đủ)
WINDOWS = {
    'AAA': ('2026-06-16', '2014-11-18', '2026-04-29', "1/65", "31/37"),
    'ABB': ('2026-03-01', '2023-07-19', '2026-02-02', "1/22", "2/31"),
    'ACB': ('2026-08-12', '2026-07-21', '2026-07-22', "1/62", "1/42"),
    'CC1': ('2026-08-19', '2025-08-06', '2026-07-31', "1/38", "2/12"),
    'DHG': ('2026-08-12', '2017-05-26', '2026-07-20', "1/77", "1/17"),
    'FPT': ('2026-08-12', '2017-07-03', '2020-04-28', "26/80", "55/97"),
    'HAH': ('2026-08-19', '2017-06-20', '2024-10-29', "8/47", "20/22"),
    'HDB': ('2026-08-12', '2026-01-28', '2026-07-31', "1/36", "1/40"),
    'HHV': ('2026-08-19', '2026-04-08', '2026-07-31', "1/27", "3/24"),
    'IDC': ('2026-06-16', '2019-04-16', '2021-02-01', "22/33", "7/8"),
    'KBC': ('2026-03-01', '2022-07-29', '2026-02-02', "1/66", "3/18"),
    'KHP': ('2026-09-14', '2020-10-08', '2026-07-20', "1/77", "7/14"),
    'MBB': ('2026-08-12', '2025-10-10', '2026-04-28', "2/60", "3/57"),
    'NAF': ('2026-01-06', '2024-11-19', '2025-10-30', "1/42", "5/28"),
    'NVL': ('2026-03-01', '2025-11-07', '2026-02-02', "1/38", "3/81"),
    'PVT': ('2026-08-12', '2025-08-01', '2026-07-29', "1/75", "2/19"),
    'TCB': ('2026-08-12', '2024-08-06', '2026-07-21', "1/34", "6/26"),
    'VCI': ('2026-03-01', '2023-05-29', '2026-02-02', "1/36", "11/42"),
    'VNM': ('2026-06-16', '2014-09-30', '2026-05-04', "1/81", "13/28"),
    'VRE': ('2026-08-19', '2018-12-26', '2026-07-29', "1/36", "1/13"),
}

_Q = {
    'AAA': [
        ('2026-04-29', '3.9374273E8'),
    ],
    'ABB': [
        ('2026-02-02', '1.397208685E9'),
    ],
    'ACB': [
        ('2026-07-22', '5.804421957E9'),
    ],
    'CC1': [
        ('2026-07-31', '4.746561E8'),
    ],
    'DHG': [
        ('2026-07-20', '1.30746071E8'),
    ],
    'FPT': [
        ('2020-04-28', '6.81668102E8'),
        ('2020-08-03', '7.8390511E8'),
        ('2020-10-26', '7.8390511E8'),
        ('2021-01-26', '7.89114878E8'),
        ('2021-04-23', '7.89114878E8'),
        ('2021-08-02', '9.07469273E8'),
        ('2021-10-25', '9.07551649E8'),
        ('2022-01-25', '9.07551649E8'),
        ('2022-04-22', '9.07551649E8'),
        ('2022-08-01', '1.097026572E9'),
        ('2022-10-25', '1.097026572E9'),
        ('2023-01-19', '1.097026572E9'),
        ('2023-04-20', '1.097026572E9'),
        ('2023-08-01', '1.269968875E9'),
        ('2023-10-19', '1.269968875E9'),
        ('2024-01-25', '1.269968875E9'),
        ('2024-04-23', '1.269968875E9'),
        ('2024-07-19', '1.460448066E9'),
        ('2024-10-24', '1.471069183E9'),
        ('2025-01-24', '1.471069183E9'),
        ('2025-04-23', '1.471069183E9'),
        ('2025-07-22', '1.703507121E9'),
        ('2025-10-24', '1.703507121E9'),
        ('2026-01-27', '1.703507121E9'),
        ('2026-04-28', '1.714326422E9'),
        ('2026-07-28', '1.714326422E9'),
    ],
    'HAH': [
        ('2024-10-29', '1.21343091E8'),
        ('2025-01-24', '1.21343091E8'),
        ('2025-04-28', '1.29894418E8'),
        ('2025-07-30', '1.29894418E8'),
        ('2025-10-30', '1.68861212E8'),
        ('2026-02-02', '1.85840401E8'),
        ('2026-05-04', '1.85840401E8'),
        ('2026-07-30', '1.91840401E8'),
    ],
    'HDB': [
        ('2026-07-31', '5.005276323E9'),
    ],
    'HHV': [
        ('2026-07-31', '5.74511888E8'),
    ],
    'IDC': [
        ('2021-02-01', '3.0E8'),
        ('2021-05-04', '3.0E8'),
        ('2021-08-02', '3.0E8'),
        ('2021-10-25', '3.0E8'),
        ('2022-02-07', '3.0E8'),
        ('2022-05-04', '3.0E8'),
        ('2022-08-01', '3.29999929E8'),
        ('2022-10-31', '3.29999929E8'),
        ('2023-01-31', '3.29999929E8'),
        ('2023-05-04', '3.29999929E8'),
        ('2023-08-01', '3.29999929E8'),
        ('2023-10-27', '3.29999929E8'),
        ('2024-01-30', '3.29999929E8'),
        ('2024-05-02', '3.29999929E8'),
        ('2024-07-30', '3.29999929E8'),
        ('2024-10-30', '3.29999929E8'),
        ('2025-01-24', '3.29999929E8'),
        ('2025-04-28', '3.29999929E8'),
        ('2025-07-30', '3.29999929E8'),
        ('2025-10-29', '3.79498823E8'),
        ('2026-01-27', '3.79498823E8'),
        ('2026-05-04', '3.79498823E8'),
    ],
    'KBC': [
        ('2026-02-02', '9.41754759E8'),
    ],
    'KHP': [
        ('2026-07-20', '6.2186518E7'),
    ],
    'MBB': [
        ('2026-04-28', '8.054999909E9'),
        ('2026-07-30', '8.054999909E9'),
    ],
    'NAF': [
        ('2025-10-30', '6.1181992E7'),
    ],
    'NVL': [
        ('2026-02-02', '2.234496474E9'),
    ],
    'PVT': [
        ('2026-07-29', '5.16918938E8'),
    ],
    'TCB': [
        ('2026-07-21', '7.086240414E9'),
    ],
    'VCI': [
        ('2026-02-02', '8.501E8'),
    ],
    'VNM': [
        ('2026-05-04', '2.089955445E9'),
    ],
    'VRE': [
        ('2026-07-29', '2.27231841E9'),
    ],
}

_C = {
    'AAA': [
        ('AIS', None, '2014-11-18', None, None, None, None, '19800000', '39600000', 'Niêm yết thêm'),
        ('ISS', '2015-09-28', None, '2015-11-05', '0.25', '9899988', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 25.0%'),
        ('AIS', None, '2015-11-05', None, None, None, None, '9899988', '49499988', 'AAA-Niêm yết thêm 9.899.988 cổ phiếu'),
        ('ISS', '2016-05-05', None, '2016-06-08', '0.0', '2000000', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('ISS', '2016-05-05', None, '2016-06-08', '0.0', '400000', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('AIS', None, '2016-06-08', None, None, None, None, '2400000', '51899988', 'AAA- Niêm yết thêm 2.400.000 cổ phiếu'),
        ('ISS', '2016-12-16', None, '2017-01-24', '0.0', '5065000', 'Phát hành cho trái chủ', None, None, 'Phát hành cổ phiếu - Phát hành cho trái chủ'),
        ('AIS', None, '2017-01-24', None, None, None, None, '5065000', '56964988', 'AAA-Niêm yết bổ sung 5.065.000 cổ phiếu'),
        ('ISS', '2017-05-30', None, '2019-06-03', '0.0', '1700000', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('ISS', '2017-06-02', None, '2017-07-28', '0.0', '585000', 'Phát hành cho trái chủ', None, None, 'Phát hành cổ phiếu - Phát hành cho trái chủ'),
        ('AIS', None, '2017-07-28', None, None, None, None, '585000', '59249988', 'AAA - Niêm yết bổ sung 585.000 cổ phiếu'),
        ('ISS', '2017-12-04', None, '2018-01-09', '0.0', '24350000', 'Phát hành cho trái chủ', None, None, 'Phát hành cổ phiếu - Phát hành cho trái chủ'),
        ('AIS', None, '2018-01-09', None, None, None, None, '24350000', '83599988', 'AAA-Niêm yết bổ sung 24.350.000 cổ phiếu'),
        ('ISS', '2018-04-09', None, '2018-06-18', '1.0', '83599988', 'Quyền mua CP cho Cổ đông hiện hữu', None, None, 'Phát hành cổ phiếu - Quyền mua CP cho Cổ đông hiện hữu tỉ lệ 100.0%'),
        ('AIS', None, '2018-06-06', None, None, None, None, '83599988', '167199976', 'AAA - Niêm yết bổ sung 83.599.988 cổ phiếu'),
        ('AIS', None, '2018-06-06', None, None, None, None, '83599988', '167199976', 'AAA - Niêm yết bổ sung 83.599.988 cổ phiếu'),
        ('ISS', '2018-09-14', None, '2018-10-18', '0.0', '4000000', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('AIS', None, '2018-10-18', None, None, None, None, '4000000', '171199976', 'AAA - Niêm yết bổ sung 4.000.000 cổ phiếu'),
        ('AIS', None, '2019-06-03', None, None, None, None, '1700000', '58664988', 'AAA-Niêm yết bổ sung 1.700.000 cổ phiếu'),
        ('ISS', '2020-07-16', None, '2020-08-12', '0.0', '40000000', 'Phát hành cho trái chủ', None, None, 'Phát hành cổ phiếu - Phát hành cho trái chủ'),
        ('AIS', None, '2020-08-12', None, None, None, None, '40000000', '211199976', 'AAA- Niêm yết bổ sung 40.000.000 cổ phiếu'),
        ('ISS', '2020-10-19', None, '2020-11-27', '0.05', '10559998', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 5.0%'),
        ('AIS', None, '2020-11-27', None, None, None, None, '10559998', '221759974', 'AAA - Niêm yết bổ sung 10.559.998 cổ phiếu'),
        ('ISS', '2021-05-04', None, '2021-06-15', '0.0', '75000000', 'Phát hành rộng rãi qua đấu giá', None, None, 'Phát hành cổ phiếu - Phát hành rộng rãi qua đấu giá'),
        ('AIS', None, '2021-06-02', None, None, None, None, '75000000', '296759974', 'AAA - Niêm yết bổ sung 358 cổ phiếu'),
        ('AIS', None, '2021-06-02', None, None, None, None, '75000000', '296759974', 'AAA - Niêm yết bổ sung 74.999.642 cổ phiếu'),
        ('ISS', '2021-09-01', None, '2021-10-12', '0.1', '29674522', 'Cổ phiếu thưởng', None, None, 'Phát hành cổ phiếu - Cổ phiếu thưởng tỉ lệ 10.0%'),
        ('AIS', None, '2021-10-12', None, None, None, None, '29674522', '326434496', 'AAA - Niêm yết bổ sung 29.674.522 cổ phiếu'),
        ('ISS', '2022-06-30', None, '2022-08-08', '0.0', '55840000', 'Phát hành rộng rãi qua đấu giá', None, None, 'Phát hành cổ phiếu - Phát hành rộng rãi qua đấu giá'),
        ('AIS', None, '2022-08-08', None, None, None, None, '55840000', '382274496', 'AAA - Niêm yết bổ sung 55,840,000 cổ phiếu'),
        ('ISS', '2025-08-29', None, '2026-08-31', '0.03', '11468234', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 3.0%'),
    ],
    'ABB': [
        ('AIS', None, '2023-07-19', None, None, None, None, '94089680', '1035036762', 'ABB - Đăng ký giao dịch bổ sung 94,089,680 cổ phiếu'),
        ('ISS', '2026-01-14', None, '2026-06-19', '0.3', '310420123', 'Quyền mua CP cho Cổ đông hiện hữu', None, None, 'Phát hành cổ phiếu - Quyền mua CP cho Cổ đông hiện hữu tỉ lệ 30.0%'),
    ],
    'ACB': [
        ('AIS', None, '2026-07-21', None, None, None, None, '667765358', '5804421957', 'ACB - Niêm yết bổ sung 667.765.358 cổ phiếu'),
    ],
    'CC1': [
        ('AIS', None, '2025-08-06', None, None, None, None, '39398275', '397906100', 'CC1 - Đăng ký giao dịch bổ sung 39.398.275 cổ phiếu'),
        ('ISS', '2026-06-17', None, '2027-06-18', '0.251315', '76750000', 'Phát hành riêng lẻ', None, None, 'Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 25.1%'),
    ],
    'DHG': [
        ('ISS', '2017-05-26', None, '2017-07-03', '0.5', '43581741', 'Cổ phiếu thưởng', None, None, 'Phát hành cổ phiếu - Cổ phiếu thưởng tỉ lệ 50.0%'),
    ],
    'FPT': [
        ('AIS', None, '2017-07-03', None, None, None, None, '69238051', '530961105', 'FPT-Niêm yết bổ sung 68.238.051 cổ phiếu'),
        ('ISS', '2018-04-03', None, '2021-04-05', '0.0', '2654556', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('AIS', None, '2018-04-23', None, None, None, None, '296525', None, 'FPT-Niêm yết bổ sung 296.525 cổ phiếu'),
        ('AIS', None, '2018-04-23', None, None, None, None, '1719317', '345695917', 'Niêm yết thêm'),
        ('ISS', '2018-05-25', None, '2018-07-24', '0.15', '80021111', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 15.0%'),
        ('AIS', None, '2018-07-16', None, None, None, None, '80021111', '613636772', 'FPT - Niêm yết thêm 80.021.111 cổ phiếu'),
        ('AIS', None, '2018-07-16', None, None, None, None, '80021111', '613636772', 'FPT - Niêm yết thêm 80.021.111 cổ phiếu'),
        ('AIS', None, '2018-07-16', None, None, None, None, '80021111', '613636772', 'FPT - Niêm yết thêm 80.021.111 cổ phiếu'),
        ('AIS', None, '2018-07-16', None, None, None, None, '80021111', '613636772', 'FPT - Niêm yết thêm 80.021.111 cổ phiếu'),
        ('ISS', '2019-04-01', None, '2022-04-01', '0.0', '3067200', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('AIS', None, '2019-04-05', None, None, None, None, '1986829', '399518469', 'FPT-Niêm yết thêm 1.986.829 cổ phiếu'),
        ('AIS', None, '2019-04-05', None, None, None, None, '297972', None, 'FPT-Niêm yết bổ sung 297.972 cổ phiếu'),
        ('ISS', '2019-05-17', None, '2019-06-28', '0.1', '61654716', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 10.0%'),
        ('AIS', None, '2019-06-24', None, None, None, None, '61654716', '678358688', 'FPT - Niêm yết bổ sung 303.673  cổ phiếu hạn chế chuyển nhượng từ ngày'),
        ('AIS', None, '2019-06-24', None, None, None, None, '61654716', '678358688', 'FPT - Niêm yết bổ sung 305.225  cổ phiếu hạn chế chuyển nhượng từ ngày'),
        ('AIS', None, '2019-06-24', None, None, None, None, '61654716', '678358688', 'FPT - Niêm yết bổ sung 306.697  cổ phiếu hạn chế chuyển nhượng từ 01/0'),
        ('AIS', None, '2019-06-24', None, None, None, None, '61654716', '678358688', 'FPT - Niêm yết bổ sung 60.739.121  cổ phiếu tự do chuyển nhượng'),
        ('ISS', '2020-03-26', None, '2023-03-27', '0.0', '3391790', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('AIS', None, '2020-04-06', None, None, None, None, '2296370', '461723054', 'FPT-Niêm yết bổ sung 2.296.370 cổ phiếu'),
        ('ISS', '2020-05-13', None, '2020-06-30', '0.15', '102237008', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 15.0%'),
        ('AIS', None, '2020-06-22', None, None, None, None, '102237008', '783987486', 'FPT- Niêm yết thêm 100.718.556 cổ phiếu'),
        ('AIS', None, '2020-06-22', None, None, None, None, '102237008', '783987486', 'FPT- Niêm yết thêm 503.681 cổ phiếu'),
        ('AIS', None, '2020-06-22', None, None, None, None, '102237008', '783987486', 'FPT- Niêm yết thêm 506.055 cổ phiếu'),
        ('AIS', None, '2020-06-22', None, None, None, None, '102237008', '783987486', 'FPT- Niêm yết thêm 508.706 cổ phiếu'),
        ('AIS', None, '2021-04-05', None, None, None, None, '2654556', '533615661', 'FPT - Niêm yết thêm 2,654,556 cổ phiếu'),
        ('ISS', '2021-04-07', None, '2024-04-08', '0.0', '3919468', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('ISS', '2021-04-07', None, '2031-04-07', '0.0', '1290300', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('AIS', None, '2021-05-18', None, None, None, None, '5209768', '789197254', 'FPT - Niêm yết bổ sung 1.290.300 cổ phiếu'),
        ('AIS', None, '2021-05-18', None, None, None, None, '5209768', '789197254', 'FPT - Niêm yết bổ sung 3.919.468 cổ phiếu'),
        ('ISS', '2021-06-01', None, '2021-07-21', '0.15', '118354395', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 15.0%'),
        ('AIS', None, '2021-07-21', None, None, None, None, '118354395', '907551649', 'FPT - Niêm yết bổ sung 118.354.395 cổ phiếu'),
        ('ISS', '2022-05-10', None, '2025-05-12', '0.0', '4537265', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('ISS', '2022-05-10', None, '2032-05-10', '0.0', '2107000', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('AIS', None, '2022-05-30', None, None, None, None, '6644265', '914195914', 'FPT - Niêm yết bổ sung 2,107,000 cổ phiếu'),
        ('AIS', None, '2022-05-30', None, None, None, None, '6644265', '914195914', 'FPT - Niêm yết bổ sung 4,537,265 cổ phiếu'),
        ('ISS', '2022-06-13', None, '2022-07-19', '0.2', '182830658', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 20.0%'),
        ('AIS', None, '2022-07-19', None, None, None, None, '182830658', '1097026572', 'FPT - Niêm yết bổ sung 182,830,658 cổ phiếu'),
        ('AIS', None, '2023-03-27', None, None, None, None, '3391790', '681780478', 'FPT - Niêm yết bổ sung 3.391.790 cổ phiếu'),
        ('ISS', '2023-05-08', None, '2033-05-09', '0.0', '1820000', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('ISS', '2023-05-08', None, '2026-05-08', '0.0', '5485050', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('AIS', None, '2023-05-31', None, None, None, None, '7305050', '1104331622', 'FPT - Niêm yết bổ sung 7,305,050 cổ phiếu'),
        ('ISS', '2023-07-05', None, '2023-08-16', '0.15', '165637253', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 15.0%'),
        ('AIS', None, '2023-08-16', None, None, None, None, '165637253', '1269968875', 'FPT - Niêm yết bổ sung 165,637,253 cổ phiếu'),
        ('ISS', '2024-06-12', None, '2024-08-01', '0.15', '190479191', 'Cổ phiếu thưởng', None, None, 'Phát hành cổ phiếu - Cổ phiếu thưởng tỉ lệ 15.0%'),
        ('AIS', None, '2024-08-01', None, None, None, None, '190479191', '1460448066', 'FPT - Niêm yết bổ sung 190,479,191 cổ phiếu'),
        ('ISS', '2024-10-09', None, '2034-10-09', '0.00227', '3319000', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.2%'),
        ('ISS', '2024-10-09', None, '2027-10-11', '0.00499', '7302117', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.5%'),
        ('AIS', None, '2025-01-02', None, None, None, None, '10621117', '1471069183', 'FPT - Niêm yết bổ sung 10.621.117 cổ phiếu'),
        ('ISS', '2025-05-07', None, '2035-05-07', '0.00225', '3315000', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.2%'),
        ('ISS', '2025-05-07', None, '2028-05-08', '0.00472', '6945939', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.5%'),
        ('AIS', None, '2025-06-19', None, None, None, None, '10260939', '1481330122', 'FPT - Niêm yết bổ sung 10.260.939 cổ phiếu'),
        ('ISS', '2025-07-21', None, '2025-09-12', '0.15', '222176999', 'Cổ phiếu thưởng', None, None, 'Phát hành cổ phiếu - Cổ phiếu thưởng tỉ lệ 15.0%'),
        ('AIS', None, '2025-09-12', None, None, None, None, '222176999', '1703507121', 'FPT - Niêm yết bổ sung 222.176.999 cổ phiếu'),
        ('ISS', '2026-06-24', None, '2036-06-24', '0.00135', '2302000', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.1%'),
        ('ISS', '2026-06-24', None, '2029-06-25', '0.00499', '8517301', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.5%'),
    ],
    'HAH': [
        ('AIS', None, '2017-06-20', None, None, None, None, '11311586', '34507818', 'HAH-Niêm yết bổ sung 11.311.586 cổ phiếu'),
        ('ISS', '2018-05-02', None, '2018-08-07', '0.5', '14274933', 'Quyền mua CP cho Cổ đông hiện hữu', None, None, 'Phát hành cổ phiếu - Quyền mua CP cho Cổ đông hiện hữu tỉ lệ 50.0%'),
        ('AIS', None, '2018-08-02', None, None, None, None, '14274933', '48782751', 'HAH - Niêm yết bổ sung 14.274.933 cổ phiếu'),
        ('AIS', None, '2018-08-02', None, None, None, None, '14274933', '48782751', 'HAH - Niêm yết bổ sung 14.274.933 cổ phiếu'),
        ('ISS', '2022-04-25', None, '2022-06-06', '0.4', '19513066', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 40.0%'),
        ('AIS', None, '2022-06-06', None, None, None, None, '19513066', '68295817', 'HAH - Niêm yết bổ sung 19,513,066 cổ phiếu'),
        ('ISS', '2022-10-27', None, '2023-10-27', '0.0', '2048850', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('ISS', '2023-08-07', None, '2023-09-08', '0.5', '35172214', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 50.0%'),
        ('AIS', None, '2023-09-08', None, None, None, None, '35172214', '105516881', 'HAH - Niêm yết bổ sung 35,172,214 cổ phiếu'),
        ('AIS', None, '2023-10-27', None, None, None, None, '2048850', '70344667', 'HAH - Niêm yết bổ sung 2,048,850 cổ phiếu'),
        ('ISS', '2024-06-21', None, '2024-07-24', '0.15', '15826210', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 15.0%'),
        ('AIS', None, '2024-07-24', None, None, None, None, '15826210', '121343091', 'HAH - Niêm yết bổ sung 15,826,210 cổ phiếu'),
        ('ISS', '2025-03-20', None, '2025-05-28', '0.0', '8551327', 'Chuyển từ trái phiếu chuyển đổi', None, None, 'Phát hành cổ phiếu - Chuyển từ trái phiếu chuyển đổi'),
        ('AIS', None, '2025-05-28', None, None, None, None, '8551327', '129894418', 'HAH - Niêm yết bổ sung 8.551.327 cổ phiếu'),
        ('ISS', '2025-08-07', None, '2025-09-09', '0.3', '38966794', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 30.0%'),
        ('AIS', None, '2025-09-09', None, None, None, None, '38966794', '168861212', 'HAH - Niêm yết bổ sung 38.966.794 cổ phiếu'),
        ('ISS', '2026-03-12', None, '2026-05-27', '0.0', '16979189', 'Chuyển từ trái phiếu chuyển đổi', None, None, 'Phát hành cổ phiếu - Chuyển từ trái phiếu chuyển đổi'),
        ('ISS', '2026-04-17', None, '2029-04-18', '0.0148', '2500000', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.5%'),
        ('AIS', None, '2026-05-27', None, None, None, None, '16979189', '185840401', 'HAH - Niêm yết bổ sung 16.979.189 cổ phiếu'),
        ('ISS', '2026-07-28', None, None, '0.01858', '3500000', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 1.9%'),
    ],
    'HDB': [
        ('AIS', None, '2026-01-28', None, None, None, None, '1145860486', '5005276323', 'HDB - Niêm yết bổ sung 1.145.860.486 cổ phiếu'),
    ],
    'HHV': [
        ('AIS', None, '2026-04-08', None, None, None, None, '49733293', '547166296', 'HHV - Niêm yết bổ sung 49.733.293 cổ phiếu'),
        ('AIS', None, '2026-05-07', None, None, None, None, '41500000', '473755528', 'HHV - Niêm yết bổ sung 41.500.000 cổ phiếu'),
        ('ISS', '2026-07-09', None, '2026-08-20', '0.05', '27345592', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 5.0%'),
    ],
    'IDC': [
        ('AIS', None, '2019-04-16', None, None, None, None, '135682500', '190988000', 'IDC - Niêm yết bổ sung 135.682.500 cổ phiếu'),
        ('AIS', None, '2019-06-13', None, None, None, None, '109012000', '300000000', 'IDC - Niêm yết bổ sung 109.012.000 cổ phiếu'),
        ('AIS', None, '2020-05-28', None, None, None, None, '108000000', '3000000000', 'IDC - Niêm yết bổ sung 108.000.000 cổ phiếu'),
        ('ISS', '2022-06-27', None, '2022-09-05', '0.1', '29999929', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 10.0%'),
        ('AIS', None, '2022-09-05', None, None, None, None, '29999929', '329999929', 'IDC - Niêm yết bổ sung 29,999,929 cổ phiếu'),
        ('ISS', '2025-08-14', None, '2025-10-03', '0.15', '49498894', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 15.0%'),
        ('AIS', None, '2025-10-03', None, None, None, None, '49498894', '379498823', 'IDC - Niêm yết bổ sung 49.498.894 cổ phiếu'),
    ],
    'KBC': [
        ('AIS', None, '2022-07-29', None, None, None, None, '191893592', '767604759', 'KBC - Niêm yết bổ sung 191,893,592 cổ phiếu'),
        ('AIS', None, '2022-10-06', None, None, None, None, '100000000', '575711167', 'KBC - Niêm yết bổ sung 100.000.000 cổ phiếu'),
        ('ISS', '2025-06-24', None, '2026-06-25', '0.3257', '174150000', 'Phát hành riêng lẻ', None, None, 'Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 32.6%'),
    ],
    'KHP': [
        ('AIS', None, '2020-10-08', None, None, None, None, '16019720', '57571016', 'KHP- Nêm yết bổ sung 16.019.720 cổ phiếu'),
        ('ISS', '2021-12-14', None, '2022-01-24', '0.025', '1400426', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 2.5%'),
        ('AIS', None, '2022-01-24', None, None, None, None, '1400426', '58971442', 'KHP - Niêm yết bổ sung 1.400.426 cổ phiếu'),
        ('ISS', '2022-05-24', None, '2022-06-28', '0.025', '1434525', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 2.5%'),
        ('AIS', None, '2022-06-28', None, None, None, None, '1434525', '60405967', 'KHP - Niêm yết bổ sung 1,434,525 cổ phiếu'),
        ('ISS', '2026-07-30', None, '2026-09-14', '0.03', '1809772', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 3.0%'),
        ('AIS', None, '2026-09-14', None, None, None, None, '1809772', '62215739', 'KHP - Niêm yết bổ sung 1.809.772 cổ phiếu'),
    ],
    'MBB': [
        ('AIS', None, '2025-10-10', None, None, None, None, '1952727250', '8054999909', 'MBB - Niêm yết bổ sung 1.952.727.250 cổ phiếu'),
        ('ISS', '2026-08-11', None, None, '0.1', '805499990', 'Quyền mua CP cho Cổ đông hiện hữu', None, None, 'Phát hành cổ phiếu - Quyền mua CP cho Cổ đông hiện hữu tỉ lệ 10.0%'),
        ('ISS', '2026-08-11', None, None, '0.15', '1208249986', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 15.0%'),
    ],
    'NAF': [
        ('AIS', None, '2024-11-19', None, None, None, None, '5056196', '55620348', 'NAF - Niêm yết bổ sung 5.056.196 cổ phiếu'),
        ('ISS', '2025-08-29', None, '2025-08-29', '0.0', '-2600000', 'Phát hành riêng lẻ', None, None, 'Phát hành cổ phiếu - Phát hành riêng lẻ'),
        ('ISS', '2025-10-09', None, '2025-11-21', '0.1', '5561706', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 10.0%'),
        ('AIS', None, '2025-11-21', None, None, None, None, '5561706', '61182054', 'NAF - Niêm yết bổ sung 5.561.706 cổ phiếu'),
        ('ISS', '2026-01-05', None, None, '0.0', '-7083933', 'Phát hành riêng lẻ', None, None, 'Phát hành cổ phiếu - Phát hành riêng lẻ'),
    ],
    'NVL': [
        ('AIS', None, '2025-11-07', None, None, None, None, '97505226', '2047609764', 'NVL - Niêm yết bổ sung 97.505.226 cổ phiếu'),
        ('ISS', '2025-12-31', None, '2026-03-06', '0.0', '20750394', 'Chuyển từ trái phiếu chuyển đổi', None, None, 'Phát hành cổ phiếu - Chuyển từ trái phiếu chuyển đổi'),
        ('ISS', '2025-12-31', None, '2027-01-04', '0.08616', '163658391', 'Phát hành riêng lẻ', None, None, 'Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 8.6%'),
    ],
    'PVT': [
        ('AIS', None, '2025-08-01', None, None, None, None, '113918597', '469931235', 'PVT - Niêm yết bổ sung 113.918.597 cổ phiếu'),
        ('ISS', '2026-06-05', None, '2026-08-20', '0.1', '46987703', 'Trả Cổ tức bằng Cổ phiếu', None, None, 'Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 10.0%'),
    ],
    'TCB': [
        ('AIS', None, '2024-08-06', None, None, None, None, '3522510811', '7045021622', 'TCB - Niêm yết bổ sung 3,522,510,811 cổ phiếu'),
        ('AIS', None, '2024-11-21', None, None, None, None, '5272297', '3522510811', 'TCB - Niêm yết bổ sung 5,272,297 cổ phiếu'),
        ('ISS', '2024-11-30', None, '2025-12-01', '0.002815', '19830117', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.3%'),
        ('ISS', '2025-08-04', None, '2026-08-05', '0.0030275', '21388675', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.3%'),
        ('AIS', None, '2025-12-01', None, None, None, None, '19830117', '7064851739', 'TCB - Niêm yết bổ sung 19.830.117 cổ phiếu'),
        ('AIS', None, '2026-08-05', None, None, None, None, '21388675', '7086240414', 'TCB - Niêm yết bổ sung 21.388.675 cổ phiếu'),
    ],
    'VCI': [
        ('AIS', None, '2023-05-29', None, None, None, None, '2000000', '335000000', 'VCI - Niêm yết bổ sung 2,000,000 cổ phiếu'),
        ('ISS', '2023-06-20', None, '2024-06-21', '0.0', '2000099', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('ISS', '2024-06-19', None, '2025-06-20', '0.0', '4400000', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('AIS', None, '2024-06-21', None, None, None, None, '2000099', '437500000', 'VCI - Niêm yết bổ sung 2,000,099 cổ phiếu'),
        ('ISS', '2024-09-12', None, '2024-10-18', '0.3', '132569480', 'Cổ phiếu thưởng', None, None, 'Phát hành cổ phiếu - Cổ phiếu thưởng tỉ lệ 30.0%'),
        ('AIS', None, '2024-10-18', None, None, None, None, '132569480', '574469480', 'VCI - Niêm yết bổ sung 132.569.480 cổ phiếu'),
        ('ISS', '2024-11-11', None, '2025-11-12', '0.250022', '143630000', 'Phát hành riêng lẻ', None, None, 'Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 25.0%'),
        ('AIS', None, '2025-06-20', None, None, None, None, '4400000', '441900000', 'VCI - Niêm yết bổ sung 4,400,000 cổ phiếu'),
        ('ISS', '2025-07-02', None, '2026-07-02', '0.00627', '4500520', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.6%'),
        ('AIS', None, '2025-11-12', None, None, None, None, '143630000', '718099480', 'VCI - Niêm yết bổ sung 143.630.000 cổ phiếu'),
        ('ISS', '2025-12-16', None, '2026-12-17', '0.176446', '127500000', 'Phát hành riêng lẻ', None, None, 'Phát hành cổ phiếu - Phát hành riêng lẻ tỉ lệ 17.6%'),
    ],
    'VNM': [
        ('AIS', None, '2014-09-30', None, None, None, None, '166685603', '1000641399', 'Niêm yết thêm'),
        ('ISS', '2015-08-05', None, '2015-09-15', '0.2', '200020794', 'Cổ phiếu thưởng', None, None, 'Phát hành cổ phiếu - Cổ phiếu thưởng tỉ lệ 20.0%'),
        ('AIS', None, '2015-09-15', None, None, None, None, '200020794', '1200662193', 'Niêm yết thêm'),
        ('ISS', '2016-07-11', None, '2019-07-15', '0.0', '8887731', 'Phát hành cho CBCNV', None, None, 'Phát hành cổ phiếu - Phát hành cho CBCNV'),
        ('ISS', '2016-08-19', None, '2016-09-20', '0.2', '241903505', 'Cổ phiếu thưởng', None, None, 'Phát hành cổ phiếu - Cổ phiếu thưởng tỉ lệ 20.0%'),
        ('AIS', None, '2016-09-20', None, None, None, None, '241903505', '1451453429', 'VNM-Niêm yết bổ sung 241.903.505 cổ phiếu'),
        ('AIS', None, '2017-07-14', None, None, None, None, '5332639', None, 'VNM-Niêm yết bổ sung 5.332.639 cổ phiếu'),
        ('AIS', None, '2018-07-16', None, None, None, None, '1777546', None, 'VNM-Niêm yết bổ sung 1.777.546 cổ phiếu'),
        ('ISS', '2018-09-05', None, '2018-10-05', '0.2', '290234364', 'Cổ phiếu thưởng', None, None, 'Phát hành cổ phiếu - Cổ phiếu thưởng tỉ lệ 20.0%'),
        ('AIS', None, '2018-10-05', None, None, None, None, '290234364', '1741687793', 'VNM - Niêm yết bổ sung 290.234.364 cổ phiếu'),
        ('AIS', None, '2019-07-15', None, None, None, None, '1777546', None, 'VNM-Niêm yết bổ sung 1.777.546 cổ phiếu'),
        ('ISS', '2020-09-29', None, '2020-11-10', '0.2', '348267652', 'Cổ phiếu thưởng', None, None, 'Phát hành cổ phiếu - Cổ phiếu thưởng tỉ lệ 20.0%'),
        ('AIS', None, '2020-11-10', None, None, None, None, '348267652', '2089955445', 'VNM - Niêm yết bổ sung 348.267.652 cổ phiếu'),
    ],
    'VRE': [
        ('AIS', None, '2018-12-26', None, None, None, None, '427739677', '2328818410', 'VRE - Niêm yết bổ sung 427.739.677 cổ phiếu'),
    ],
}


def frozen(tickers):
    """(quarters, corp) ĐÚNG hình dạng `oshares_live._fetch(tickers, until)` — dòng dict, sắp theo
    mã (ORDER BY ticker), dict MỚI mỗi lần gọi. Mã không có trong fixture ⇒ KeyError (không bao
    giờ âm thầm trả rỗng: rỗng là một câu trả lời hợp lệ của `oshares_at`, lỗi thì không)."""
    s = sorted(set([tickers] if isinstance(tickers, str) else tickers))
    missing = [t for t in s if t not in _Q]
    if missing:
        raise KeyError(f"mã chưa đóng băng trong oshares_selfcheck_fixture: {missing}")
    return ([dict(zip(("ticker",) + Q_COLS, (t,) + r)) for t in s for r in _Q[t]],
            [dict(zip(("ticker",) + C_COLS, (t,) + r)) for t in s for r in _C[t]])
