from pymongo import MongoClient


def connect_mongo():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['taxcode_db']
    return db


def get_taxcode_in_queue():
    db = connect_mongo()
    taxcode_collection = db['taxcodes']
    taxcode_queue_collection = db['taxcodes_queue']
    total_taxcode = taxcode_collection.count_documents({})
    batch_size = 1000
    count = 0
    for i in range(0, total_taxcode, batch_size):
        cursor = taxcode_collection.find({}, {'_id': 0}).skip(i).limit(batch_size)
        collection = list(cursor)
        taxcode_list = [item['taxcode'] for item in collection]
        
        data_inserted = {
            'taxcodes': taxcode_list,
            'status': 'pending',
            'last_taxcode': None,
            'updated_last_taxcode_time': None,
            'created_time': None,
        }

        taxcode_queue_collection.insert_one(data_inserted)
        count += 1
        print(f'[INFO] Inserted {len(taxcode_list)} taxcodes in queue, count = {count}')


if __name__ == '__main__':
    get_taxcode_in_queue()