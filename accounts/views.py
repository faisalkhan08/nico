from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from accounts.models import Users
import pandas as pd
import json
import csv, io
import matplotlib.pyplot as plt
from django.http import HttpResponse, JsonResponse
from accounts.models import Templates, ColorSet, ColorCode, ChartType
import os
from matplotlib_venn import venn2, venn2_circles
from matplotlib_venn import venn3, venn3_circles
from django.core.mail import send_mail


class HomePage(View):

    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'index.html')
        return render(request, 'login.html')


class Login(View):

    def get(self, request):
        if request.user.is_superuser:
            return render(request, 'index.html')
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('email')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('/')
            else:
                messages.warning(request, 'Username or Password Incorrect.')
                return render(request, 'login.html')
        else:
            messages.warning(request, 'Please enter username and password.')
            return render(request, 'login.html')


class Logout(View):

    def get(self, request):
        logout(request)
        return redirect('accounts:login')


class PasswordResetView(View):

    def get(self, request):
        return render(request, 'forgot-password.html')


def password_reset_request(request):
    if request.method == "POST":
        domain = request.headers['Host']
        data = request.POST.get('email')
        associated_users = Users.objects.filter(username=data)
        if associated_users.exists():
            for user in associated_users:
                subject = "Password Reset Requested"
                email_template_name = "/home/nisl/WORKING_DIRECTORY/dvwp/dvwp/accounts/templates/password_reset_email.txt"
                c = {
                    "email": user.email,
                    'domain': domain,
                    'site_name': 'Website',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                }
                email = render_to_string(email_template_name, c)
                try:
                    send_mail(subject, email, 'noreply7jan@gmail.com', [user.email], fail_silently=False)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                return redirect("/password_reset/done/")

    password_reset_form = PasswordResetForm()
    return render(request, '',
                  context={"password_reset_form": password_reset_form})


class UserManagementList(View):

    def get(self, request):
        users = Users.objects.filter(is_superuser=False)
        context = {
            'users': users
        }
        return render(request, 'user-management.html', context=context)

    def post(self, request):

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        position = request.POST.get('position')
        department = request.POST.get('department')
        confirm_password = request.POST.get('confirm_password')
        obj = Users.objects.create(username=email, email=email, first_name=first_name, last_name=last_name,
                                   position=position, department=department, phone_number=number)
        obj.set_password(str(confirm_password))
        obj.save()
        body = 'Username : ' + email + '\nPassword : ' + confirm_password + '\n'
        send_mail('subject', body, 'noreply7jan@gmail.com',
                  [str(email)])
        data = {}
        data['Status'] = 200
        data['message'] = 'Successfully Created'
        return JsonResponse(data, safe=False)



class EditUser(View):

    def get(self, request, id):
        try:
            obj = Users.objects.get(id=id)
            dic = {}
            dic['first_name'] = obj.first_name
            dic['last_name'] = obj.last_name
            dic['email'] = obj.email
            dic['phone_number'] = obj.phone_number
            dic['position'] = obj.position
            dic['department'] = obj.department
            dic['id'] = obj.id
            dic['status'] = 200
            return JsonResponse(dic)

        except Exception as e:
            messages.warning(request, "Form have some error" + str(e))
            return JsonResponse({"message": "Form have some error" + str(e), "status": "400"}, safe=False)

    def post(self, request, id):
        try:
            obj = Users.objects.get(id=id)
            obj.first_name = request.POST.get("first_name")
            obj.last_name = request.POST.get("last_name")
            obj.email = request.POST.get("email")
            obj.phone_number = request.POST.get("phone_number")
            obj.position = request.POST.get("position")
            obj.department = request.POST.get("department")
            obj.save()
            context = {
                'user': obj,
                'status': 200
            }
            return JsonResponse(context)

        except Exception as e:
            messages.warning(request, "Form have some error" + str(e))
            return JsonResponse({"message": "Form have some error" + str(e), "status": "400"}, safe=False)


class TemplatesManagementList(View):

    def get(self, request):
        temp = Templates.objects.filter(created_by=request.user)
        context = {
            'temp': temp
        }
        return render(request, 'template_management.html', context=context)


class DeleteUser(View):

    def get(self, request, id):
        users = Users.objects.get(id=id).delete()
        return redirect('accounts:user_manangement_list')


class DeleteColourSet(View):

    def get(self, request, id):
        users = ColorSet.objects.get(id=id).delete()
        return redirect('accounts:create_color_set')


class DeleteTemp(View):

    def get(self, request, id):
        temp = Templates.objects.get(id=id).delete()
        return redirect('accounts:template_management_list')


class EditTemplate(View):

    def get(self, request, id):
        obj = Templates.objects.get(id=id)
        file = obj.source_file
        med = pd.read_csv(file)
        sales = pd.DataFrame(med)
        data = []
        for i in list(sales):
            dic = {}
            dic['data'] = sales[i].tolist()
            dic['label'] = sales[i].name
            data.append(dic)
        dic = {}
        dic['variable'] = obj.variable
        dic['scale_x'] = obj.scale_x
        dic['scale_y'] = obj.scale_y
        dic['scale_step'] = obj.scale_step
        dic['labeling_title'] = obj.labeling_title
        dic['labeling_x'] = obj.labeling_x
        dic['labeling_y'] = obj.labeling_y
        dic['legends'] = obj.legends
        dic['alignment'] = obj.alignment
        dic['chart_type'] = obj.chart_type
        dic['colour_set_id'] = obj.color.id
        colour_set = obj.color
        colour_list = []
        for i in colour_set.color_code.all():
            colour_list.append(i.colour)
        dic['colour_list'] = colour_list
        context = {
            'data': data,
            'dic': dic
        }
        return render(request, 'edit_template.html', context=context)

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from io import StringIO
from io import BytesIO
import base64, urllib
class CreateGraphic(View):

    def get(self, request):
        return render(request, 'create-graphics.html')

    def post(self, request):
        if request.POST.get('chart_type') == "line":
            file = request.FILES.get('file')
            med = pd.read_csv(file)
            sales = pd.DataFrame(med)
            data = []
            for i in list(sales):
                # show the list of values
                # if request.POST.get('label') == sales[i].name:
                dic = {}
                dic['data'] = sales[i].tolist()
                dic['label'] = sales[i].name
                data.append(dic)

            return JsonResponse(data, safe=False)
            # sales.to_json(orient='split')
            # print(data)
            # print(sales.to_json(orient='records'))
        elif request.POST.get('chart_type') == "bar":
            file = request.FILES.get('file')
            med = pd.read_csv(file)
            sales = pd.DataFrame(med)
            data = []
            for i in list(sales):
                dic = {}
                dic['data'] = sales[i].tolist()
                dic['label'] = sales[i].name
                data.append(dic)

            return JsonResponse(data, safe=False)
        elif request.POST.get('chart_type') == "pie":
            file = request.FILES.get('file')
            med = pd.read_csv(file)
            sales = pd.DataFrame(med)
            data = []
            for i in list(sales):
                dic = {}
                dic['data'] = sales[i].tolist()
                dic['label'] = sales[i].name
                data.append(dic)
            return JsonResponse(data, safe=False)
        elif request.POST.get('chart_type') == "horizontalBar":
            file = request.FILES.get('file')
            med = pd.read_csv(file)
            sales = pd.DataFrame(med)
            data = []
            for i in list(sales):
                dic = {}
                dic['data'] = sales[i].tolist()
                dic['label'] = sales[i].name
                data.append(dic)
            return JsonResponse(data, safe=False)
        elif request.POST.get('chart_type') == "venn_diagram":
            file = request.FILES.get('file')
            if 'colour_list' in request.POST:
                colour_list = request.POST.get('colour_list').split(',')
            else:
                colour_list = ''
            if 'title' in request.POST:
                title = request.POST.get('title').split(',')
            else:
                title = ''
            med = pd.read_csv(file)
            sales = pd.DataFrame(med)
            data = []
            label = []
            y = 0
            for i in list(sales):
                if y != 0:
                    data.append(sales[i].tolist())
                    label.append(sales[i].name)
                y = y + 1

            if colour_list:
                venn3([set(data[0]), set(data[1]), set(data[2])], set_labels=set(label),
                      set_colors=set(colour_list))
            else:
                venn3([set(data[0]), set(data[1]), set(data[2])],
                      set_labels=set(label),
                      set_colors=("#ff0000", "#5ba1d7", "#4af25d", "#d054d9"))

            plt.tight_layout()
            if title:
                plt.title(str(title))

            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()

            graphic = base64.b64encode(image_png)
            graphic = graphic.decode('utf-8')

            context = {}
            context['graphic'] = graphic
            return JsonResponse(context, safe=False)


class CreateColorSet(View):

    def get(self, request):
        try:
            obj = ColorSet.objects.all()
            list_set = []
            for i in obj:
                dic = {}
                dic['colour_set_name'] = i.color_set_name
                dic['description'] = i.description

                dic['id'] = i.id
                chart = i.chart_type.all()
                chart_list = []
                for z in chart:
                    chart_list.append(z.chart)
                dic['chart_list'] = chart_list

                colour = i.color_code.all()
                colour_list = []
                for j in colour:
                    colour_list.append(j.colour)
                dic['colour_list'] = colour_list
                list_set.append(dic)

            context = {
                'obj': list_set
            }
            return render(request, 'color-management.html', context=context)
        except Exception as e:
            messages.warning(request, "Form have some error" + str(e))
            return JsonResponse({"message": "Form have some error" + str(e), "status": "400"}, safe=False)

    def post(self, request):
        try:
            color_set_name = request.POST.get('color_set_name')
            description = request.POST.get('descriptions')
            chart_type = request.POST.getlist('chart_type[]')
            color_code_list = request.POST.getlist('colour_array[]')
            obj = ColorSet.objects.create(color_set_name=color_set_name, description=description)
            for i in chart_type:
                name = str(i).replace('×', ' ')
                chart_obj = ChartType()
                chart_obj.chart = str(name).strip()
                chart_obj.save()
                obj.chart_type.add(chart_obj)

            for rec in color_code_list:
                color_obj = ColorCode()
                color_obj.colour = rec
                color_obj.save()
                obj.color_code.add(color_obj)
            obj.save()
            return JsonResponse({"message": "Successfully Created.", "status": "200"}, safe=False)
        except Exception as e:
            messages.warning(request, "Form have some error" + str(e))
            return JsonResponse({"message": "Form have some error" + str(e), "status": "400"}, safe=False)


class EditColorSet(View):

    def get(self, request, id):
        try:
            obj = ColorSet.objects.get(id=id)
            dic = {}
            dic['colour_set_name'] = obj.color_set_name
            dic['description'] = obj.description
            dic['chart_type'] = obj.chart_type
            colour = obj.color_code.all()
            colour_list = []
            for j in colour:
                colour_list.append(j.colour)
            dic['colour_list'] = colour_list
            return JsonResponse(dic, safe=False)
        except Exception as e:
            messages.warning(request, "Form have some error" + str(e))
            return JsonResponse({"message": "Form have some error" + str(e), "status": "400"}, safe=False)

    def post(self, request):
        try:
            color_set_name = request.POST.get('color_set_name')
            description = request.POST.get('descriptions')
            chart_type = request.POST.getlist('chart_type[]')
            id = request.POST.get('id')
            color_code_list = request.POST.getlist('colour_array[]')
            obj = ColorSet.objects.get(id=id)
            obj.color_set_name = color_set_name
            obj.description = description
            if chart_type:
                obj.chart_type.clear()
                for i in chart_type:
                    name = str(i).replace('×', ' ')
                    chart_obj = ChartType()
                    chart_obj.chart = str(name).strip()
                    chart_obj.save()
                    obj.chart_type.add(chart_obj)

            if color_code_list:
                obj.color_code.clear()
                for rec in color_code_list:
                    color_obj = ColorCode()
                    color_obj.colour = rec
                    color_obj.save()
                    obj.color_code.add(color_obj)
            obj.save()
            return JsonResponse({"message": "Successfully Created.", "status": "200"}, safe=False)
        except Exception as e:
            messages.warning(request, "Form have some error" + str(e))
            return JsonResponse({"message": "Form have some error" + str(e), "status": "400"}, safe=False)


class CreateTemplate(View):

    def post(self, request):
        try:
            file = request.FILES.get('file')
            charts_type = request.POST.get('charts_type')
            if file and charts_type:
                variable = request.POST.get('set')
                max_scale = request.POST.get('max_scale')
                min_scale = request.POST.get('min_scale')
                step_size = request.POST.get('step_size')
                align = request.POST.get('align')
                legend = request.POST.get('legend')
                title = request.POST.get('title')
                x_axes = request.POST.get('x_axes')
                y_axes_ = request.POST.get('y_axes')
                colour_set_id = request.POST.get('colour_set_id')
                obj = Templates.objects.create(created_by=request.user, source_file=file, chart_type=charts_type, variable=variable,
                                               scale_step=step_size, scale_x=min_scale, scale_y=max_scale,
                                               alignment=align, legends=legend, labeling_title=title, labeling_x=x_axes,
                                               labeling_y=y_axes_)
                try:
                    colour_set = ColorSet.objects.get(id=colour_set_id)
                    obj.color = colour_set
                    obj.save()
                except Exception as e:
                    messages.warning(request, "Form have some error" + str(e))
                    return JsonResponse({"message": "Form have some error" + str(e), "status": "400"}, safe=False)

                return JsonResponse({"message": "Successfully Created.", "status": "200"}, safe=False)
            else:
                return JsonResponse({"message": "file and chart type is not valid", "status": "400"}, safe=False)

        except Exception as e:
            messages.warning(request, "Form have some error" + str(e))
            return JsonResponse({"message": "Form have some error" + str(e), "status": "400"}, safe=False)


class UserCsv(View):

    def post(self, request):
        try:
            file = request.FILES.get('file')
            if not file.name.endswith('.csv'):
                messages.error(request, 'THIS IS NOT A CSV FILE')
            data_set = file.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            for column in csv.reader(io_string, delimiter=',', quotechar="|"):
                print(column)
                # obj = Users.objects.create(username=column[0], email=column[0], first_name=column[1], last_name=column[2],
                #                            position=column[4], department=column[5], phone_number=column[3])
            return JsonResponse({"message": "Successfully Created.", "status": "200"}, safe=False)
        except Exception as e:
            messages.warning(request, "Form have some error" + str(e))
            return JsonResponse({"message": "Form have some error" + str(e), "status": "400"}, safe=False)


def list_of_colourset(request):
    if request.method == "GET":
        obj = ColorSet.objects.all()
        list_set = []
        for i in obj:
            colour = i.color_code.all()
            dic = {}
            dic['colour_set_name'] = i.color_set_name
            dic['id'] = i.id
            colour_list = []
            for j in colour:
                colour_list.append(j.colour)
            dic['colour_list'] = colour_list
            list_set.append(dic)
        return JsonResponse(list_set, safe=False)

from sklearn import datasets
import numpy as np
def create_graph(request):
    obj = Templates.objects.get(id=4)
    file = obj.source_file
    med = pd.read_csv(file)
    sales = pd.DataFrame(med)
    data = []
    label_list = []
    colour_list = []
    for i in obj.color.color_code.all():
        print(i.colour)
        hex = str(i.colour).lstrip('#')
        colour = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
        colour_list.append(i.colour)
    y = 0
    for i in list(sales):
        dic = {}
        print(sales.iloc[y].tolist())
        dic['data'] = sales.iloc[y].tolist()
        dic['label'] = sales[i].name
        dic['color'] = colour_list[y]
        label_list.append(sales[i].name)
        data.append(dic)
        y = y + 1

    #horizontal Bar
    barh = []
    dic = {}
    z = 0
    for i in list(sales):
        dic[str(sales[i].name)] = sales.iloc[z].tolist()
        barh.append(dic)
        z = z + 1

    df = pd.DataFrame(dic, columns=label_list, index=label_list,)
    plt.style.use('ggplot')

    df.plot.barh(color=colour_list)

    plt.title('Store Inventory')
    plt.ylabel('Product')
    plt.xlabel('Quantity')
    plt.show()

    # For Bar Chart
    # N = len(data[1]['data'])
    # ind = np.arange(N)  # the x locations for the groups
    # width = 0.20  # the width of the bars
    #
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # #
    # #
    # yvals = data[0]['data']
    # rects1 = ax.bar(ind, yvals, width, color="#ff0000")
    # zvals = data[1]['data']
    # rects2 = ax.bar(ind + width, zvals, width, color='#5ba1d7')
    # kvals = data[2]['data']
    # rects3 = ax.bar(ind + width * 2, kvals, width, color='#4af25d')
    # #
    # #
    # ax.set_ylabel('Scores')
    # ax.set_xticks(ind + width)
    # ax.set_xticklabels(tuple(label_list))
    # plt.title("Bar Chart Iris Averages")
    # plt.xlabel("X-label")
    # plt.ylabel("Y-label")
    # plt.ylim([10, 100])
    # plt.legend()
    # plt.show()

    # For Line Chart
    # ax = plt.subplot(111)
    # labels = data[0]['data']
    # bp_dict = ax.bar(data[1]['data'], labels, align='center')
    # bp_dict = ax.bar(data[2]['data'], labels, align='center')
    # bp_dict = ax.bar(data[3]['data'], labels, align='center')
    # plt.title("Bar Chart Iris Averages")
    # plt.ylabel("Average")
    # plt.show()

    # for i in data:
    #     plt.plot(label_list, i['data'], label=i['label'], marker='o', c=i['color'])



    # plt.plot(data[0]['data'], data[1]['data'], label=data[1]['label'], marker='o')
    # plt.plot(data[0]['data'], data[2]['data'], label=data[2]['label'], marker='o')
    # plt.plot(data[0]['data'], data[3]['data'], label=data[3]['label'], marker='o')
    # plt.title("X-label")
    # plt.xlabel("X-label")
    # plt.ylabel("Y-label")
    # plt.ylim([10, 100])
    # plt.legend()
    # plt.show()


def generate_code(request):
    try:
        file = request.FILES.get('file')
        charts_type = request.POST.get('charts_type')
        if file and charts_type:
            variable = request.POST.get('set')
            max_scale = request.POST.get('max_scale')
            min_scale = request.POST.get('min_scale')
            step_size = request.POST.get('step_size')
            align = request.POST.get('align')
            legend = request.POST.get('legend')
            title = request.POST.get('title')
            x_axes = request.POST.get('x_axes')
            y_axes_ = request.POST.get('y_axes')
            colour_set_id = request.POST.get('colour_set_id')
            if colour_set_id != "undefined":
                obj = ColorSet.objects.get(id=colour_set_id)
                color_list = obj.color_code.all()
            else:
                color_list = ["#ff0000", "#5ba1d7", "#4af25d", "#d054d9", "#3cb9a4"]
            med = pd.read_csv(file)
            sales = pd.DataFrame(med)

            if charts_type == "line":
                data = []
                label_list = []
                y = 0
                for i in list(sales):
                    dic = {}
                    print(sales.iloc[y].tolist())
                    dic['data'] = sales.iloc[y].tolist()
                    dic['label'] = sales[i].name
                    if colour_set_id != "undefined":
                        dic['color'] = color_list[y].colour
                    else:
                        dic['color'] = color_list[y]
                    label_list.append(sales[i].name)
                    data.append(dic)
                    y = y + 1

                filepath = os.getcwd()
                file_name = "generate.py"
                temp_path = filepath + "/" + file_name
                if temp_path:
                    os.remove(temp_path)
                file = open(file_name, 'w')
                file.write('import matplotlib.pyplot as plt\n')
                file.write('import numpy as np\n')
                file.write('import matplotlib\n')
                file.write('matplotlib.use("TkAgg")\n')
                file.write('\n')
                file.write('\n')
                file.write('def MakeFile():\n')
                if variable != "Show All":
                    for i in data:
                        label = str(i['label'])
                        if variable == label:
                            file.write('\tplt.plot(' + str(label_list) + ',' + str(i['data']) + ', label="' + str(
                                label) + '", marker="o", c="' + str(i['color']) + '")\n')
                else:
                    for i in data:
                        if color_list:
                            label = str(i['label'])
                            file.write('\tplt.plot(' + str(label_list) + ',' + str(i['data']) + ', label="' + str(
                                label) + '", marker="o", c="' + str(i['color']) + '")\n')
                        else:
                            label = str(i['label'])
                            file.write('\tplt.plot(' + str(label_list) + ',' + str(i['data']) + ', label="' + str(label) + '", marker="o")\n')
                if x_axes:
                    file.write('\tplt.xlabel("' + str(x_axes) + '")\n')

                if y_axes_:
                    file.write('\tplt.xlabel("' + str(y_axes_) + '")\n')

                if title:
                    file.write('\tplt.title("' + str(title) + '")\n')

                if min_scale and max_scale:
                    file.write('\tplt.ylim([' + str(min_scale) + ',' + str(max_scale) + '])\n')
                file.write('\tplt.legend()\n')
                file.write('\tplt.show()\n')
                file.write('\n')
                file.write('\n')
                file.write('if __name__ == "__main__":\n')
                file.write('\tMakeFile()\n')
                file.close()
                file = open('/home/nisl/WORKING_DIRECTORY/dvwp/dvwp/generate.py', 'rb')
                response = HttpResponse(file)
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment;filename="/home/nisl/WORKING_DIRECTORY/dvwp/dvwp/generate.py"'
                return response

            if charts_type == 'bar':
                data = []
                label_list = []
                y = 0
                for i in list(sales):
                    dic = {}
                    print(sales.iloc[y].tolist())
                    dic['data'] = sales.iloc[y].tolist()
                    dic['label'] = sales[i].name
                    if colour_set_id != "undefined":
                        dic['color'] = color_list[y].colour
                    else:
                        dic['color'] = color_list[y]
                    label_list.append(sales[i].name)
                    data.append(dic)
                    y = y + 1
                filepath = os.getcwd()
                file_name = "generate.py"
                temp_path = filepath + "/" + file_name
                if temp_path:
                    os.remove(temp_path)
                file = open(file_name, 'w')
                file.write('import matplotlib.pyplot as plt\n')
                file.write('import numpy as np\n')
                file.write('import matplotlib\n')
                file.write('matplotlib.use("TkAgg")\n')
                file.write('\n')
                file.write('\n')
                file.write('def MakeFile():\n')
                length = len(data[1]['data'])
                file.write('\tN = ' + str(length) + '\n')
                ind = np.arange(length)
                file.write('\tind = np.arange(N)\n')
                width = 0.20
                file.write('\twidth = 0.20 \n')
                file.write('\tfig = plt.figure() \n')
                file.write('\tax = fig.add_subplot(111) \n')
                z = 0
                if variable and variable != "Show All":
                    for i in data:
                        label = str(i['label'])
                        if variable == label:
                            yvals = i['data']
                            file.write('\tax.bar(ind, ' + str(yvals) + ', ' + str(width) + ', color="' + str(i['color']) + '" )\n')
                else:
                    for i in data:
                        if z == 0:
                            yvals = i['data']
                            file.write('\tax.bar(ind, ' + str(yvals) + ', ' + str(width) + ', color="' + str(i['color']) + '" )\n')
                        elif z == 1:
                            yvals = i['data']
                            file.write('\tax.bar(ind + width, ' + str(yvals) + ', ' + str(width) + ', color="' + str(i['color']) + '" )\n')
                        else:
                            yvals = i['data']
                            file.write('\tax.bar(ind + width * ' + str(z) + ',' + str(yvals) + ', ' + str(width) + ', color="' + str(i['color']) + '" )\n')
                        z = z + 1
                file.write('\tax.set_xticks(ind + width)\n')
                file.write('\tax.set_xticklabels(tuple(' + str(label_list) + '))\n')

                if x_axes:
                    file.write('\tplt.xlabel("' + str(x_axes) + '")\n')

                if y_axes_:
                    file.write('\tplt.xlabel("' + str(y_axes_) + '")\n')

                if title:
                    file.write('\tplt.title("' + str(title) + '")\n')

                if min_scale and max_scale:
                    file.write('\tplt.ylim([' + str(min_scale) + ',' + str(max_scale) + '])\n')

                file.write('\tplt.legend()\n')
                file.write('\tplt.show()\n')
                file.write('\n')
                file.write('\n')
                file.write('if __name__ == "__main__":\n')
                file.write('\tMakeFile()\n')
                file.close()
                file = open('/home/nisl/WORKING_DIRECTORY/dvwp/dvwp/generate.py', 'rb')
                response = HttpResponse(file)
                response['Content-Type'] = 'application/octet-stream'
                response[
                    'Content-Disposition'] = 'attachment;filename="/home/nisl/WORKING_DIRECTORY/dvwp/dvwp/generate.py"'
                return response

            if charts_type == 'horizontalBar':
                dic = {}
                label_list = []
                z = 0
                for i in list(sales):
                    dic[str(sales[i].name)] = sales.iloc[z].tolist()
                    label_list.append(sales[i].name)
                    z = z + 1

                filepath = os.getcwd()
                file_name = "generate.py"
                temp_path = filepath + "/" + file_name
                if temp_path:
                    os.remove(temp_path)
                file = open(file_name, 'w')
                file.write('import matplotlib.pyplot as plt\n')
                file.write('import numpy as np\n')
                file.write('import pandas as pd\n')
                file.write('import matplotlib\n')
                file.write('matplotlib.use("TkAgg")\n')
                file.write('\n')
                file.write('\n')
                file.write('def MakeFile():\n')
                file.write('\tdic = ' + str(dic) + ' \n')
                file.write('\tlabel_list = ' + str(label_list) + ' \n')
                file.write('\tdf = pd.DataFrame(dic, columns=label_list, index=label_list)\n')
                file.write('\tplt.style.use("ggplot")\n')
                file.write('\tdf.plot.barh(color=' + str(color_list) + ')\n')
                if x_axes:
                    file.write('\tplt.xlabel("' + str(x_axes) + '")\n')

                if y_axes_:
                    file.write('\tplt.xlabel("' + str(y_axes_) + '")\n')

                if title:
                    file.write('\tplt.title("' + str(title) + '")\n')
                file.write('\tplt.legend()\n')
                file.write('\tplt.show()\n')
                file.write('\n')
                file.write('\n')
                file.write('if __name__ == "__main__":\n')
                file.write('\tMakeFile()\n')
                file.close()
                file = open('/home/nisl/WORKING_DIRECTORY/dvwp/dvwp/generate.py', 'rb')
                response = HttpResponse(file)
                response['Content-Type'] = 'application/octet-stream'
                response[
                    'Content-Disposition'] = 'attachment;filename="/home/nisl/WORKING_DIRECTORY/dvwp/dvwp/generate.py"'
                return response

            if charts_type == 'venn_diagram':
                data = []
                label_list = []
                y = 0
                for i in list(sales):
                    if y != 0:
                        data.append(sales[i].tolist())
                        label_list.append(sales[i].name)
                    y = y + 1

                filepath = os.getcwd()
                file_name = "generate.py"
                temp_path = filepath + "/" + file_name
                if temp_path:
                    os.remove(temp_path)
                file = open(file_name, 'w')
                file.write('import matplotlib.pyplot as plt\n')
                file.write('from matplotlib_venn import venn2, venn2_circles\n')
                file.write('from matplotlib_venn import venn3, venn3_circles\n')
                file.write('import numpy as np\n')
                file.write('import pandas as pd\n')
                file.write('import matplotlib\n')
                file.write('matplotlib.use("TkAgg")\n')
                file.write('\n')
                file.write('\n')
                file.write('def MakeFile():\n')
                file.write('\tvenn3([' + str(set(data[0])) + ', ' + str(set(data[1])) + ', ' + str(
                    set(data[2])) + '], set_labels=' + str(set(label_list)) + ', set_colors=' + str(set(color_list)) + ')\n')
                if title:
                    file.write('\tplt.title("' + str(title) + '")\n')
                file.write('\tplt.legend()\n')
                file.write('\tplt.show()\n')
                file.write('\n')
                file.write('\n')
                file.write('if __name__ == "__main__":\n')
                file.write('\tMakeFile()\n')
                file.close()
                file = open('/home/nisl/WORKING_DIRECTORY/dvwp/dvwp/generate.py', 'rb')
                response = HttpResponse(file)
                response['Content-Type'] = 'application/octet-stream'
                response[
                    'Content-Disposition'] = 'attachment;filename="/home/nisl/WORKING_DIRECTORY/dvwp/dvwp/generate.py"'
                return response

            if charts_type == "pie":
                data = []
                for i in list(sales):
                    dic = {}
                    dic['data'] = sales[i].tolist()
                    dic['label'] = sales[i].name
                    data.append(dic)

                filepath = os.getcwd()
                file_name = "generate.py"
                temp_path = filepath + "/" + file_name
                if temp_path:
                    os.remove(temp_path)
                file = open(file_name, 'w')
                file.write('import matplotlib.pyplot as plt\n')
                file.write('from matplotlib_venn import venn2, venn2_circles\n')
                file.write('from matplotlib_venn import venn3, venn3_circles\n')
                file.write('import numpy as np\n')
                file.write('import pandas as pd\n')
                file.write('import matplotlib\n')
                file.write('matplotlib.use("TkAgg")\n')
                file.write('\n')
                file.write('\n')
                file.write('def MakeFile():\n')
                file.write('\ty = np.array(' + str(data[1]['data']) +')\n')
                file.write('\tmylabels = ' + str(data[0]['data']) + '\n')
                file.write('\tmycolors = ' + str(color_list) + '\n')
                file.write('\tplt.pie(y, labels=mylabels, colors=mycolors)\n')
                if title:
                    file.write('\tplt.title("' + str(title) + '")\n')
                file.write('\tplt.legend()\n')
                file.write('\tplt.show()\n')
                file.write('\n')
                file.write('\n')
                file.write('if __name__ == "__main__":\n')
                file.write('\tMakeFile()\n')
                file.close()
                file = open('/home/nisl/WORKING_DIRECTORY/dvwp/dvwp/generate.py', 'rb')
                response = HttpResponse(file)
                response['Content-Type'] = 'application/octet-stream'
                response[
                    'Content-Disposition'] = 'attachment;filename="/home/nisl/WORKING_DIRECTORY/dvwp/dvwp/generate.py"'
                return response

    except Exception as e:
        messages.warning(request, "Form have some error" + str(e))
        return JsonResponse({"message": "Form have some error" + str(e), "status": "400"}, safe=False)