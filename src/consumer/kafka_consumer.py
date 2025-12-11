from kafka import KafkaConsumer
import json
import psycopg2
import pickle
import pandas as pd

def run_consumer():
    # --- Load model ---
    with open("model_top5.pkl", "rb") as f:
        model = pickle.load(f)

    # --- Lấy đúng thứ tự FEATURE mà model đã train ---
    MODEL_FEATURES = model.get_booster().feature_names
    print("Model feature order:", MODEL_FEATURES)

    # --- Kết nối PostgreSQL ---
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="loan_default_db",
        user="postgres",
        password="postgres"
    )
    cursor = conn.cursor()

    # --- Kafka consumer ---
    consumer = KafkaConsumer(
        'loan_data',
        group_id='loan_consumer_group',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    for message in consumer:
        try:
            data = message.value

            # --- Chuẩn bị features theo đúng thứ tự model ---
            df_pred = pd.DataFrame([data])
            X = df_pred.reindex(columns=MODEL_FEATURES, fill_value=0)

            # --- Dự đoán nhãn ---
            default_flag = int(model.predict(X)[0])

            # --- Ghi vào Database ---
            cursor.execute(f"""
                INSERT INTO loan_risk_features (
                    {",".join(MODEL_FEATURES)},
                    default_flag
                )
                VALUES ({",".join(["%s"] * (len(MODEL_FEATURES) + 1))})
            """, (
                *[data.get(col, 0) for col in MODEL_FEATURES],
                default_flag
            ))

            conn.commit()
            print(f"Inserted with default_flag={default_flag}: {data}")

        except Exception as e:
            print(f"Error processing message: {e}")
            continue

    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_consumer()
