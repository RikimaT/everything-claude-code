"""
Optimal Time Engine: Calculate best posting times based on engagement
"""
import sqlite3
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json

class OptimalTimeEngine:
    def __init__(self, db_path: str = "bridge_data.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize timing analysis table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posting_times (
                id INTEGER PRIMARY KEY,
                platform TEXT,
                posted_hour INTEGER,
                posted_day_of_week INTEGER,
                engagement_score REAL,
                recorded_at TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def record_engagement(self, platform: str, posted_at: datetime,
                         likes: int, comments: int):
        """Record engagement for a post"""
        engagement_score = likes + (comments * 2)  # Comments weighted more

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO posting_times
            (platform, posted_hour, posted_day_of_week, engagement_score, recorded_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            platform,
            posted_at.hour,
            posted_at.weekday(),
            engagement_score,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    def analyze_optimal_times(self, platform: str) -> Dict:
        """Analyze optimal posting times for platform"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT posted_hour, posted_day_of_week, AVG(engagement_score) as avg_score
            FROM posting_times
            WHERE platform = ?
            GROUP BY posted_hour, posted_day_of_week
            ORDER BY avg_score DESC
        ''', (platform,))

        results = cursor.fetchall()
        conn.close()

        analysis = {
            "best_hours": {},
            "best_days": {},
            "overall_avg": 0
        }

        if not results:
            # Use defaults if no data
            return self._get_default_times(platform)

        # Aggregate by hour
        hour_scores = {}
        for hour, day, score in results:
            if hour not in hour_scores:
                hour_scores[hour] = []
            hour_scores[hour].append(score)

        analysis["best_hours"] = {
            h: sum(s) / len(s) for h, s in hour_scores.items()
        }

        # Aggregate by day
        day_scores = {}
        for hour, day, score in results:
            if day not in day_scores:
                day_scores[day] = []
            day_scores[day].append(score)

        analysis["best_days"] = {
            d: sum(s) / len(s) for d, s in day_scores.items()
        }

        analysis["overall_avg"] = sum(s for h, s in analysis["best_hours"].items()) / len(analysis["best_hours"]) if analysis["best_hours"] else 0

        return analysis

    def _get_default_times(self, platform: str) -> Dict:
        """Get default optimal times for platforms"""
        defaults = {
            "x": {
                "best_hours": {
                    7: 45,    # Morning
                    12: 50,   # Lunch
                    18: 55,   # Evening
                    21: 48    # Night
                },
                "best_days": {
                    0: 45,    # Mon
                    1: 48,    # Tue
                    2: 50,    # Wed
                    3: 47,    # Thu
                    4: 52,    # Fri
                    5: 40,    # Sat
                    6: 35     # Sun
                }
            },
            "threads": {
                "best_hours": {
                    9: 50,
                    14: 48,
                    19: 52,
                    21: 45
                },
                "best_days": {
                    0: 48,
                    1: 50,
                    2: 49,
                    3: 47,
                    4: 52,
                    5: 42,
                    6: 38
                }
            },
            "instagram": {
                "best_hours": {
                    7: 40,
                    12: 50,
                    18: 55,
                    20: 52
                },
                "best_days": {
                    0: 45,
                    1: 48,
                    2: 50,
                    3: 49,
                    4: 52,
                    5: 43,
                    6: 40
                }
            }
        }

        return defaults.get(platform, defaults["x"])

    def calculate_next_optimal_time(self, platform: str, today: datetime = None) -> datetime:
        """Calculate next optimal posting time"""
        if today is None:
            today = datetime.now()

        analysis = self.analyze_optimal_times(platform)

        # Get best hour for today
        best_hours = sorted(analysis["best_hours"].items(), key=lambda x: x[1], reverse=True)

        # Add some randomness (±30 min) to avoid pattern detection
        best_hour = best_hours[0][0] if best_hours else 18
        minute = random.randint(0, 59)

        # Check if time has passed today
        posting_time = today.replace(hour=best_hour, minute=minute, second=0)

        if posting_time < datetime.now():
            # Use next day
            posting_time = (today + timedelta(days=1)).replace(hour=best_hour, minute=minute)

        return posting_time

    def generate_schedule(self, platform: str, days_ahead: int = 7) -> List[Tuple[datetime, float]]:
        """Generate posting schedule for next N days"""
        schedule = []
        today = datetime.now()

        analysis = self.analyze_optimal_times(platform)
        best_hours = sorted(analysis["best_hours"].items(), key=lambda x: x[1], reverse=True)[:3]

        for i in range(days_ahead):
            current_date = today + timedelta(days=i)

            # Rotate through best hours
            best_hour = best_hours[i % len(best_hours)][0]
            minute = random.randint(15, 45)

            posting_time = current_date.replace(hour=best_hour, minute=minute)
            score = best_hours[i % len(best_hours)][1]

            schedule.append((posting_time, score))

        return schedule

    def export_schedule(self, platform: str, output_file: str = None):
        """Export posting schedule to JSON"""
        if output_file is None:
            output_file = f"{platform}_schedule.json"

        schedule = self.generate_schedule(platform, days_ahead=14)
        schedule_data = [
            {
                "datetime": dt.isoformat(),
                "readable": dt.strftime("%Y-%m-%d %H:%M"),
                "score": round(score, 2)
            }
            for dt, score in schedule
        ]

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=2)

        print(f"✓ Schedule exported to {output_file}")


if __name__ == "__main__":
    print("⏰ Optimal Time Engine")
    print("-" * 50)

    engine = OptimalTimeEngine()

    # Generate schedule for each platform
    for platform in ["x", "threads", "instagram"]:
        print(f"\n📅 Generating schedule for {platform.upper()}...")
        engine.export_schedule(platform)

        # Show next posting time
        next_time = engine.calculate_next_optimal_time(platform)
        print(f"   Next optimal time: {next_time.strftime('%Y-%m-%d %H:%M')}")

    print("\n✅ Schedule generation complete!")
