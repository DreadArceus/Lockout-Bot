import discord
import os
import traceback

from discord.ext import commands
from discord.ext.commands import cooldown, BucketType

from data import dbconn
from utils import cf_api, discord_, codeforces

MAX_PROBLEMS = 20
LOWER_RATING = 800
UPPER_RATING = 3500
MAX_TAGS = 5
MAX_ALTS = 5


class Random(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.db = dbconn.DbConn()
        self.cf = cf_api.CodeforcesAPI()

    @commands.command(name="suggest")
    async def suggest(self, ctx, *users: discord.Member):
        users = list(set(users))
        if len(users) == 0:
            await discord_.send_message(ctx, f"The correct usage is `;suggest @user1 @user2...`")
            return
        if ctx.author not in users:
            users.append(ctx.author)
        for i in users:
            if not self.db.get_handle(ctx.guild.id, i.id):
                await discord_.send_message(ctx, f"Handle for {i.mention} not set! Use `;handle identify` to register")
                return

        problem_cnt = await discord_.get_time_response(self.client, ctx,
                                                       f"{ctx.author.mention} enter the number of problems per rating "
                                                       f"between [1, {MAX_PROBLEMS}]",
                                                       30, ctx.author, [1, MAX_PROBLEMS])
        if not problem_cnt[0]:
            await discord_.send_message(ctx, f"{ctx.author.mention} you took too long to decide")
            return
        problem_cnt = problem_cnt[1]

        rating = await discord_.get_seq_response(self.client, ctx, f"{ctx.author.mention} enter space seperated "
                                                                   f"lowerbound and upperbound ratings of problems ("
                                                                   f"between {LOWER_RATING} and {UPPER_RATING})", 60,
                                                 2, ctx.author, [LOWER_RATING, UPPER_RATING])
        if not rating[0]:
            await discord_.send_message(ctx, f"{ctx.author.mention} you took too long to decide")
            return
        rating = rating[1]

        handles = [self.db.get_handle(ctx.guild.id, x.id) for x in users]
        problems = []
        r = rating[0]
        while r <= rating[1]:
            problems.append(await codeforces.find_problems(handles, [r]*problem_cnt))
            r += 100
        if not problems[0]:
            await discord_.send_message(ctx, problems[1])
            return
        problems = problems[1]

        print(problems)


def setup(client):
    client.add_cog(Random(client))
