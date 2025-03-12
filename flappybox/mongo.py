from pymongo import MongoClient
import server

# Replace with your own connection string
def mongo_server():
    connection_string = "mongodb+srv://boss:@cluster0.cu9qeko.mongodb.net"
    client = MongoClient(connection_string)
    db = client['mydatabase']  # Replace 'mydatabase' with your database name
    collection = db['mycollection']  # Replace 'mycollection' with your collection name
    
    while True:
        try:
            data = input("Enter data to store in MongoDB: ")

            document = {'message': data}
            collection.insert_one(document) #inserts 1 doc into collection

            print('Data stored in MongoDB')
        except KeyboardInterrupt:
            break

    client.close()

if __name__ == "__main__":
    mongo_server()