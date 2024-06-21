from django.utils.timezone import now
from .models import User, LoginActivity

def get_site_statistics():
    users = User.objects.all()
    data = []
    for user in users:
        last_login_activity = LoginActivity.objects.filter(user=user).last()
        is_online = last_login_activity and not last_login_activity.logout_time
        data.append({
            'id': user.id,
            'username': user.username,
            'login_count': user.login_count,
            'total_time_spent': user.total_time_spent,
            'is_online': is_online
        })
    return data

def calculate_90th_percentile(scores):
    try:
        if scores:
            scores.sort()
            percentile_index = int(len(scores) * 0.9) - 1
            return scores[percentile_index]
    except:
        return None
    return None

def update_login_count_and_activity(user):
    user.login_count += 1
    user.save()
    LoginActivity.objects.create(user=user, login_time=now())

def record_logout_and_calculate_time_spent(user):
    login_activity = LoginActivity.objects.filter(user=user, logout_time__isnull=True).first()
    if login_activity:
        login_activity.logout_time = now()
        login_activity.save()
        session_duration = login_activity.logout_time - login_activity.login_time
        user.total_time_spent += session_duration
        user.save()
    return login_activity
