WITH p AS (SELECT ticker, time, Price, Close, LAG(Price) OVER w AS p0, LAG(Close) OVER w AS c0
  FROM tav2_pin.ticker_pin_202610 WHERE time BETWEEN '2009-12-01' AND '2014-12-31' WINDOW w AS (PARTITION BY ticker ORDER BY time))
SELECT ticker, time, p0, Price, c0, Close, ROUND(Price/p0-1,3) AS rp, ROUND(Close/c0-1,3) AS rc FROM p
WHERE time >= '2010-01-01' AND Price/p0-1 < -0.20 AND ticker IN ('VNM','FPT','HPG','MSN','DHG','PNJ','REE','SSI','VCB','MWG','GAS','DPM','HAG','KDC','BVH','VIC','CTG','EIB','STB','ACB')
ORDER BY rp LIMIT 20
