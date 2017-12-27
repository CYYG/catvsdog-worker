import redis
import psycopg2
import json
import os

def voteWorker(event, context):
    redisClient = redis.Redis(host=os.getenv('REDIS_HOST', default='redis'), port=6379, db=0)

    print("REDIS_HOST: %s", (os.getenv('REDIS_HOST', default='redis')))
    newJSONVote = redisClient.lpop('votes')

    if newJSONVote:
        newVote = json.loads(newJSONVote)
        voterId = newVote['voter_id']
        voterVote = newVote['vote']

        pgClient = psycopg2.connect(dbname="postgres", user="postgres", password="postgres", host=os.getenv('PG_HOST', default='localhost'))
        pgCursor = pgClient.cursor()
        pgCursor.execute("CREATE TABLE IF NOT EXISTS votes (id VARCHAR(255) NOT NULL UNIQUE,vote VARCHAR(255) NOT NULL)")
        pgCursor.execute("INSERT INTO votes (id, vote) VALUES (%s, %s) ON CONFLICT (id) DO UPDATE SET vote = %s", (voterId, voterVote, voterVote))
        pgClient.commit()
        pgCursor.close()
        pgClient.close()
