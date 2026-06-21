from pymongo import MongoClient

MONGO_URI = "mongodb://192.168.100.7:27017"
DB_NAME = "hyperopt_db"
COLLECTION_NAME = "jobs"


def update_exp_key(
        mongo_uri: str,
        db_name: str,
        collection_name: str,
        old_exp_key: str,
        new_exp_key: str
):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    col = db[collection_name]

    # Xóa các document với exp_key=old_exp_key và loss != Infinity
    # col.delete_many({
    #     "exp_key": old_exp_key,
    #     "result.loss": {"$ne": float("inf")}
    # })

    # Update exp_key mới cho các document còn lại với exp_key=old_exp_key
    col.update_many(
        {
            "exp_key": old_exp_key,
            "result.loss": float("inf")
        },
        {"$set": {"exp_key": new_exp_key}}
    )

    client.close()


# Ví dụ sử dụng:
if __name__ == "__main__":
    patterns = ['BKMA200', 'Conservative', 'BuySupport', 'TrendingGrowth', 'TL3M', 'RSILow30', 'UnderBV',
                'SuperGrowth', 'SurpriseEarning', 'VolMax1Y', 'DividendYield']
    patterns = ['BuySupport']
    for pattern in patterns:
        old_exp_key = f"trials_buy_{pattern}_v4"
        new_exp_key = f"trials_buy_{pattern}_v5"
        update_exp_key(MONGO_URI, DB_NAME, COLLECTION_NAME, old_exp_key, new_exp_key)
