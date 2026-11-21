import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import gzip
import pandas as pd
from datetime import datetime
from backend.app.config import settings
from backend.app.database import engine, SessionLocal, Base
from backend.app.models.entities import Stop, Route, HourlyDemand, ModelEvaluation, SimulationScenario

def seed():
    print(f"Creating database tables on: {settings.DATABASE_URL} ...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        # 1. Seed Stops
        stops_file = os.path.join(settings.DATA_DIR, 'stops_meta.json')
        if os.path.exists(stops_file):
            print("Seeding stops...")
            with open(stops_file, 'r') as f:
                stops_data = json.load(f)
            stop_objs = []
            for s in stops_data:
                stop_objs.append(Stop(
                    name=s['name'],
                    latitude=s['latitude'],
                    longitude=s['longitude'],
                    corridor=s['corridor'],
                    monthly_boardings=s['monthly_boardings'],
                    monthly_alightings=s['monthly_alightings'],
                    is_major_hub=s['is_major_hub']
                ))
            session.bulk_save_objects(stop_objs)
            session.commit()
            print(f"Seeded {len(stop_objs)} stops.")

        # 2. Seed Routes
        routes_file = os.path.join(settings.PROCESSED_DATA_DIR, 'route_profiles.json')
        if not os.path.exists(routes_file):
            routes_file = os.path.join(settings.DATA_DIR, 'routes_meta.json')
        if os.path.exists(routes_file):
            print(f"Seeding routes from {routes_file}...")
            with open(routes_file, 'r') as f:
                routes_data = json.load(f)
            route_objs = []
            for r in routes_data:
                route_objs.append(Route(
                    route_id=r['route_id'],
                    direction=r['direction'],
                    origin=r['origin'],
                    destination=r['destination'],
                    total_tickets=r['total_tickets'],
                    total_passengers=r['total_passengers'],
                    total_revenue=r['total_revenue'],
                    is_predominantly_ac=r['is_predominantly_ac'],
                    avg_daily_passengers=r['avg_daily_passengers']
                ))
            session.bulk_save_objects(route_objs)
            session.commit()
            print(f"Seeded {len(route_objs)} routes.")

        # 3. Seed Hourly Demand (Sample / Prominent routes for fast querying)
        hourly_file = os.path.join(settings.PROCESSED_DATA_DIR, 'hourly_route_demand.csv.gz')
        if not os.path.exists(hourly_file):
            hourly_file = os.path.join(settings.DATA_DIR, 'hourly_route_demand.csv.gz')
        if os.path.exists(hourly_file):
            print(f"Seeding hourly demand table from {hourly_file}...")
            df = pd.read_csv(hourly_file, compression='gzip')
            # Select top 50,000 hourly rows covering all major routes for responsive database querying
            df_sample = df.sample(n=min(50000, len(df)), random_state=42)
            demand_objs = []
            for _, row in df_sample.iterrows():
                demand_objs.append(HourlyDemand(
                    route_id=str(row['route']),
                    date=str(row['date']),
                    day_of_week=int(row['day_of_week']),
                    hour=int(row['hour']),
                    is_weekend=int(row['is_weekend']),
                    passengers=int(row['passengers']),
                    tickets=int(row['tickets']),
                    revenue=float(row['revenue']),
                    ac_trips=int(row['ac_trips'])
                ))
            session.bulk_save_objects(demand_objs)
            session.commit()
            print(f"Seeded {len(demand_objs)} hourly demand records.")

        # 4. Seed Model Evaluation
        eval_file = os.path.join(settings.MODELS_DIR, 'evaluation_metrics.json')
        if os.path.exists(eval_file):
            print("Seeding model evaluation metrics...")
            with open(eval_file, 'r') as f:
                eval_data = json.load(f)
            evaluation = ModelEvaluation(
                model_name=eval_data['model_name'],
                dataset_split=eval_data['dataset_split'],
                train_samples=eval_data['train_samples'],
                test_samples=eval_data['test_samples'],
                mae=eval_data['mae'],
                rmse=eval_data['rmse'],
                r2_score=eval_data['r2_score'],
                baseline_mae=eval_data['baseline_mae'],
                improvement_pct=eval_data['improvement_pct'],
                feature_importance_json=json.dumps(eval_data.get('features', []))
            )
            session.add(evaluation)
            session.commit()
            print("Seeded model evaluation.")

        # 5. Default Simulation baseline
        scenario = SimulationScenario(
            name="Baseline Network Operation",
            demand_multiplier=1.0,
            peak_shift_factor=0.0,
            result_summary=json.dumps({"status": "nominal", "network_stress": "moderate"})
        )
        session.add(scenario)
        session.commit()

        print("Database seeding completed successfully!")
    except Exception as e:
        session.rollback()
        print(f"Error during database seed: {e}")
        raise e
    finally:
        session.close()

if __name__ == '__main__':
    seed()
