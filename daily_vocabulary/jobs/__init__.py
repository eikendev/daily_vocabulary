from . import frequent


def register_jobs(jq):
    jq.run_repeating(frequent.job_subscription, 60, first=10)
