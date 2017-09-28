from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from .models import Activity, ActivityUser, Type, Image,Avatar
from .forms import ActivityForm, UploadFileForm
from django.utils.dateparse import parse_datetime
from  datetime  import  *
import csv
import re #多个关键字分割句子


def index(request):
    return render(request, 'index.html')

@login_required
def homepage(request):
    activities_added = []
    activities_choosen = []
    activities_set1 = ActivityUser.objects.all().filter(user=request.user, status='A')
    activities_set2 = ActivityUser.objects.all().filter(user=request.user, status='P')
    for item in activities_set1:
        activities_added.append(item.activity)
    for item in activities_set2:
        activities_choosen.append(item.activity)
    activities_added = sorted(activities_added,key=lambda Activity: Activity.begin_time)
    return render(request, 'homepage.html', {'activities_added': activities_added, 'activities_choosen': activities_choosen})

@login_required
def manage(request):
    activities_view = []
    activities_choosen = []
    # 用户已经选择的活动和已经安排的活动
    activities_choosen_set = ActivityUser.objects.all().filter(Q(user=request.user, status='P')|Q(user=request.user,status='A'))
    for item in activities_choosen_set:
        activities_choosen.append(item.activity)
    # 可选的活动包括该用户可见的私有活动，和没有被选中的公有活动
    activities_view_set = ActivityUser.objects.all().filter(user=request.user, status='V')
    for item in activities_view_set:
        activities_view.append(item.activity)
    public_activities = list(Activity.objects.all().filter(is_public=True))
    choosen_public_activities_set = ActivityUser.objects.all().filter(Q(user=request.user, status='P')|Q(user=request.user,status='A'))
    if choosen_public_activities_set.exists():
        for item in choosen_public_activities_set:
            d = item.activity
            if d in public_activities:
                public_activities.remove(d)
    for item in public_activities:
        activities_view.append(item)
    #print(activities_choosen)
    return render(request, 'manage.html', {'activities_view': activities_view,
                  'activities_choosen': activities_choosen})

@login_required
def activity(request, idActivity):
    activity = get_object_or_404(Activity, pk=idActivity)
    user = request.user
    #两个布尔变量控制按钮的显示形式
    #是否可以删除
    if user == activity.creator:
        can_delete=True
    else:
        can_delete=False
    #是否可以加入，只有状态为V的活动才可以加入
    can_join=True
    s = ActivityUser.objects.filter(user=user, activity=activity)
    if s.exists():
        for item in s:
            if item.status=='P' or item.status=='A':
                can_join=False
    return render(request, 'activity.html', {'activity': activity, 'idActivity': idActivity,'can_delete':can_delete,'can_join':can_join})

@login_required
def activity_submit(request, idActivity):
    activity = get_object_or_404(Activity, pk=idActivity)
    if activity.is_public:
        p = ActivityUser.objects.create(status='P', user=request.user, activity=activity,priority = request.POST['priority'])
        p.save()
    else:
        p = ActivityUser.objects.get(user=request.user, activity=activity)
        p.status = 'P'
        p.priority=request.POST['priority']
        p.save()
    return redirect('manage')
@login_required
def activity_unsubmit(request, idActivity):
    activity = get_object_or_404(Activity, pk=idActivity)
    if activity.is_public:
        p = ActivityUser.objects.get(user=request.user, activity=activity)
        p.delete()
    else:
        p = ActivityUser.objects.get(user=request.user, activity=activity)
        p.status = 'V'
        p.save()
    return redirect('manage')
@login_required
def activity_delete(request, idActivity):
    activity = get_object_or_404(Activity, pk=idActivity)
    print(activity)
    activity.delete()
    return redirect('manage')

@login_required
def userinfo(request):
    avatar = get_object_or_404(Avatar, user=request.user)
    return render(request, 'userinfo.html', {'avatar': avatar})

@login_required
def create(request):
    params = request.POST if request.method == 'POST' else None
    form = ActivityForm(params, request.FILES)
    print(request.POST)
    if form.is_valid():
        activity = form.save(commit=False)
        activity.creator = request.user
        activity.duration = activity.end_time - activity.begin_time
        if request.POST['map_location']:
            activity.location = request.POST['map_location']
        else:
            activity.location = '北京'
        activity.save()
        if 'image' in request.FILES:
            image = Image(
            image=request.FILES['image'],
            activity=activity,
        )
        else:
            image = Image(activity=activity,)
        image.save()
        messages.success(request, '{}创建成功'.format(activity.title))
        form = ActivityForm()
        if activity.is_public == False:
            au = ActivityUser(activity=activity, user=request.user, status='V')
            au.save()
    types = Type.objects.all()
    return render(request, 'create.html', {'form': form, 'types': types})


def login(request):
    return render(request, 'login.html')


def authenticate(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = auth.authenticate(request, username=username,
                             password=password)
    if not user:
        messages.info(request,'账号或密码错误')
        return redirect('index')

    auth.login(request, user)
    return redirect('help')


def signup(request):
    return render(request, 'signup.html')


def signup_submit(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')

    try:
        user = User.objects.create_user(username=username, password=password, email=email)
        auth.login(request, user)
        avatar = Avatar(user=user)
        avatar.save()
        return redirect('help')
    except:
        messages.info(request, '用户名{}已存在'.format(username))
        return redirect('index')


@login_required
def logout(request):
    auth.logout(request)
    return redirect('index')

@login_required
def search(request):
    types = Type.objects.all()
    return render(request, 'search.html',{'types':types})
@login_required
def search_result(request):
    types = Type.objects.all()
    activities = []
    candidate_list=list(Activity.objects.filter(is_public=True))
    user_candidate_list_set = ActivityUser.objects.filter(user=request.user)

    for item in user_candidate_list_set:
        if item.activity not in candidate_list:
            candidate_list.append(item.activity)
    #通过关键词进行检索
    if request.POST['keyWords']:
        word_list = re.split(',|，',request.POST['keyWords'])
        for item in range(len(candidate_list)-1,-1,-1):
            to_delete=True
            for word in word_list:
                if candidate_list[item].title.find(word)!=-1:
                    to_delete=False
            if to_delete==True:
                del candidate_list[item]
    #活动时长
    if request.POST['duration']=='1':
        for item in range(len(candidate_list)-1,-1,-1):
            if candidate_list[item].duration > timedelta(hours=1):
                del candidate_list[item]
    elif request.POST['duration']=='2':
        for item in range(len(candidate_list)-1,-1,-1):
            if timedelta(hours=1) > candidate_list[item].duration or candidate_list[item].duration > timedelta(hours=3):
                del candidate_list[item]
    elif request.POST['duration']=='3':
        for item in range(len(candidate_list)-1,-1,-1):
            if candidate_list[item].duration < timedelta(hours=3):
                del candidate_list[item]
    #活动类别
    if(request.POST['type']!='0'):
        type_set = Type.objects.all()
        for type_item in type_set:
            if request.POST['type']==type_item.content:
                target_type = type_item.content
        for item in range(len(candidate_list)-1,-1,-1):
            if candidate_list[item].type.content!=target_type:
                del candidate_list[item]

    activities = candidate_list
    #开始日期
    if request.POST['begin_time']:
        target_time=datetime.strptime(request.POST['begin_time'],"%Y-%m-%d")
        for item in range(len(candidate_list)-1,-1,-1):
            if candidate_list[item].begin_time.year!=target_time.year or candidate_list[item].begin_time.month!=target_time.month or candidate_list[item].begin_time.day!=target_time.day:
                del candidate_list[item]
    #活动标签(标签中含搜索的词语)
    if request.POST['tag']:
        tag_list = re.split(',|，',request.POST['tag'])
        for item in range(len(candidate_list)-1,-1,-1):
            to_delete=True
            for word in tag_list:
                if candidate_list[item].tags.find(word)!=-1:
                    to_delete=False
            if to_delete==True:
                del candidate_list[item]
    activities=candidate_list
    return render(request, 'search.html', {'activities':activities,'types':types})

def exception(request):
    return render(request, 'exception.html')

def handle_uploaded_file(request, f):
    with open('tmp_upload_file', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
    with open('tmp_upload_file', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            #print(row)
            a = Activity(
                title=row['title'],
                description=row['description'],
                begin_time=parse_datetime(row['begin_time']),
                end_time=parse_datetime(row['end_time']),
                is_public=True if row['is_public'] == 'True' else False,
                location=row['location'],
                type=get_object_or_404(Type, content=row['type']),
                creator=request.user,
            )
            a.duration = a.end_time - a.begin_time
            a.save()
            img = Image(activity=a, )
            img.save()

            if row['is_public'] == 'False':
                au = ActivityUser(
                    activity=a,
                    user=request.user,
                    status='V',
                )
                au.save()

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request, request.FILES['file'])
            messages.info(request, '活动导入成功')
            # return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


def Prev(A, k):
    key = A[k]
    i = k - 1
    while i >= 0 and A[i].end_time > key.begin_time:
        i -= 1
    if i < 0:
        return None
    else:
        return i


def Next(A, k):
    key = A[k]
    i = k + 1
    while i <= len(A) - 1 and A[i].begin_time < key.end_time:
        i += 1
    if i > len(A) - 1:
        return None
    else:
        return i


def schedule_by_priority(request, optimal_result, A, i, j):
    if (str(i) + '-' + str(j)) in optimal_result:
        return optimal_result[str(i) + '-' + str(j)][0]
    if i == None or j == None:
        return 0
    if i == j:
        optimal_result.update(
            {str(i) + '-' + str(j): [ActivityUser.objects.get(user=request.user, activity=A[i]).priority, i]})
        return ActivityUser.objects.get(user=request.user, activity=A[i]).priority
    if i > j: return 0
    max = 0
    for k in range(i, j + 1):
        k1 = Prev(A, k)
        k2 = Next(A, k)
        #print(k1)
        #print(k2)
        w = schedule_by_priority(request, optimal_result, A, i, k1) + schedule_by_priority(request, optimal_result, A, k2,
                                                                   j) + ActivityUser.objects.get(user=request.user,
                                                                                      activity=A[k]).priority
        #print('w:')
        #print(w)
        if w > max:
            max = w
            option = k
    optimal_result.update({str(i) + '-' + str(j): [max, option]})
    return max
def schedule_by_amount(request, optimal_result, A, i, j):
    if (str(i) + '-' + str(j)) in optimal_result:
        return optimal_result[str(i) + '-' + str(j)][0]
    if i == None or j == None:
        return 0
    if i == j:
        optimal_result.update(
            {str(i) + '-' + str(j): [ActivityUser.objects.get(user=request.user, activity=A[i]).enthusiasm, i]})
        return ActivityUser.objects.get(user=request.user, activity=A[i]).enthusiasm
    if i > j: return 0
    max = 0
    for k in range(i, j + 1):
        k1 = Prev(A, k)
        k2 = Next(A, k)
        w = schedule_by_amount(request, optimal_result, A, i, k1) + schedule_by_amount(request, optimal_result, A, k2,
                                                                   j) + ActivityUser.objects.get(user=request.user,
                                                                                                 activity=A[k]).enthusiasm
        if w > max:
            max = w
            option = k
    optimal_result.update({str(i) + '-' + str(j): [max, option]})
    return max

def get_result(request, A, optimal_result, destlist, i, j):
    if (str(i) + '-' + str(j)) not in optimal_result:
        return
    t = optimal_result[(str(i) + '-' + str(j))][1]
    destlist.append(A[t])
    t1 = Prev(A, t)
    t2 = Next(A, t)
    get_result(request, A, optimal_result, destlist, i, t1)
    get_result(request, A, optimal_result, destlist, t2, j)


# dp_schedule中是动态规划算法，从数据库中取出所有状态为被选中的数据，计算出选中的活动，再将被选中的活动标记为已选中
#by_priority最后获得结果权重之和最大，by_amount最后获得结果活动数量最多（使用enthusiasm)
def dp_schedule_by_priority(request):
    # 初始化，将所有状态为“已添加”的都还原为"已选择"
    print("priority")
    t1 = ActivityUser.objects.all().filter(user=request.user, status='A')
    if t1.exists():
        for item in t1:
            item.status = 'P'
            item.save()
    query_set = ActivityUser.objects.all().filter(user=request.user, status='P')
    if query_set.exists()==False:
        return redirect('exception')
    activity_list = []
    for item in query_set:
        activity_list.append(item.activity)
    activity_list = sorted(activity_list, key=lambda Activity: Activity.begin_time)
    optimal_result = {}
    optimal_activity_list = []
    a = schedule_by_priority(request, optimal_result, activity_list, 0, len(activity_list) - 1)
    get_result(request, activity_list, optimal_result, optimal_activity_list, 0, len(activity_list) - 1)
    # optimal_activity_list中储存的是选中的活动(类型为Activity)
    # 改变数据库中活动的状态为“已安排”
    for item in optimal_activity_list:
        t = ActivityUser.objects.get(user=request.user, activity=item)
        t.status = 'A'
        t.save()
    return redirect('homepage')
def dp_schedule_by_amount(request):
     # 初始化，将所有状态为“已添加”的都还原为"已选择"
    print("amount")
    t1 = ActivityUser.objects.all().filter(user=request.user, status='A')
    if t1.exists():
        for item in t1:
            item.status = 'P'
            item.save()
    query_set = ActivityUser.objects.all().filter(user=request.user, status='P')
    if query_set.exists()==False:
        return redirect('exception')
    activity_list = []
    for item in query_set:
        activity_list.append(item.activity)
    activity_list = sorted(activity_list, key=lambda Activity: Activity.begin_time)
    optimal_result = {}
    optimal_activity_list = []
    a = schedule_by_amount(request, optimal_result, activity_list, 0, len(activity_list) - 1)
    get_result(request, activity_list, optimal_result, optimal_activity_list, 0, len(activity_list) - 1)
    # optimal_activity_list中储存的是选中的活动(类型为Activity)
    # 改变数据库中活动的状态为“已安排”
    for item in optimal_activity_list:
        t = ActivityUser.objects.get(user=request.user, activity=item)
        t.status = 'A'
        t.save()
    return redirect('homepage')

@login_required
def userinfo_submit(request):
    if request.POST['email']:
        user = get_object_or_404(User, username=request.user)
        user.email = request.POST['email']
        user.save()
    if request.FILES['avatar']:
        avatar = get_object_or_404(Avatar, user=request.user)
        avatar.avatar=request.FILES['avatar']
        avatar.save()
    
    return redirect('userinfo')
def help(request):
    return render(request,'help.html')
