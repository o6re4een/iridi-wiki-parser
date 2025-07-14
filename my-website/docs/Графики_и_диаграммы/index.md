# Графики и диаграммы

##  Линейные графики \(Linear Trend\) 

**Linear Trend** \(линейная диаграмма\) – это график изменения переменной, на котором точки – значения переменной, соединены между собой линией\. На графике можно отображать изменение нескольких переменных во времени\. 

График отображает значения **из базы данных iRidium server** , из внешней базы данных, или массива, сформированного с помощью JavaScript\. Ряд параметров линейной диаграммы доступен для изменения из скриптов\. 

Приложение i3 pro не сохраняет собственную базу данных, поэтому графики обычно отображают информацию, полученную от iRidium server\. 

**Настройка графиков** 

1. сохраните историю изменения фидбека в базу данных iRidium server
1. настройте отображение истории на графике: создайте графический элемент Linear Trend в интерфейсе i3 pro, и свяжите его с фидбеком сервера, историю которого отображаете

###  1\. Сохраните историю фидбека в базу данных iRidium server 

Записать в базу можно Feedback драйвера или виртуальный Feedback\. Настройки сохранения в базу доступны в проекте логики для iRidium server: 

![123](/img/Графики_и_диаграммы/Studio2019_Server_Save_to_DB.png)

Параметры сохранения в базу данных: 

- **Persist** – сохранять последнее значение, записанное в переменную, и воспроизводить его сразу при перезагрузки сервера до стартовой инициализации драйверов\. С помощью этого параметра загрузка значений происходит без лишних скачков, при работе с графиком факт выключения / перезагрузки сервера не будет зафиксирован в нём\.
- **Store In DB** – включить сохранение переменной в базу данных, выбрать формат данных 

    - *None* – запись в базу выключена
    - *Signed 32bit* – записывать как целое число со знаком
    - *Float 64bit* – записывать как число с плавающей запятой
    - *String UTF8* – записывать как строку
- **Load On Start** \- записать последнее значение переменной из базы данных в фидбек при запуске сервера;
- **DB Save Strategy** \- стратегия сохранения данных: выберите тип события, при котором создается запись в базу: 

    - *Deadband* – сохранение при изменении переменной на значение, отличное от предыдущего на указанную величину или больше\. 

        - *Deadband \(значение\)* – минимальное изменение переменной, при котором производится запись в базу\. В стратегии Deadband: 0, новая запись формируется при любом отличии получаемых значений, и не формируется, если в переменную повторно приходит одно и то же число\.
    - *Interval* – периодическое сохранение\. Запись создается с указанным временным интервалом; 

        - *Interval \(значение\)* – выберите интервал записи от 5 секунд до 1 часа, или укажите вручную \(Custom\) в мс\. Если в Store In DB указана строка \(String UTF8\), запись будет формироваться 1 раз в минуту, настроить более частое сохранение нельзя \(используйте стратегию Deadband\);
        - *Interval Value* \- значение интервала \(минимально 1\);
        - *Interval Units* \- единицы измерения;
- **Forward value to** \- перенаправление значения из одного тега в другой \(подробнее [здесь ](https://dev.iridi.com/Forward_value_to)\);
- **On Server** \- включить / выключить связь тега с панельным проектом \(в выключенном состоянии тег не будет отображаться в панельном проекте и учитываться в лицензии\)\.

Сохранение по интервалу удобно использовать для переменных, которые изменяются плавно и достаточно инертны, например – температура и влажность воздуха\. 

Сохранение "по изменению" подходит для переменных, у которых важно не пропустить момент изменения\. Например, можно записать в базу включения и выключение света, изменения скорости вращения вентилятора\. 

###  2\. Отобразите историю переменной на графике 

Создайте графический элемент **Linear Trend** в интерфейсе i3 pro, и свяжите его с фидбеком сервера, историю которого отображаете: 

![123](/img/Графики_и_диаграммы/Studio2019_Server_Trend_Feedbacks.png)

**Двойным кликом** по элементу откройте **настройки внешнего вида и размаха** графика и каждой его кривой: 

![123](/img/Графики_и_диаграммы/Studio2019_Server_Trend_Settings.png)

**Основные настройки** графика \(General\): 

- **Горизонтальная ось \(время\)** 

    - **Range** – размах уровня по оси времени
    - **Position** – размещение оси времени: сверху или снизу от графика
    - **Make marks by** – засечки на графике, с указанным интервалом в сек/мин/ч/дн
    - **Divisions between marks** – количество подпунктов между засечками
- **Вертикальная ось \(данные\)** 

    - **Auto\-scaling** – авто\-масштабирование шкалы от нуля до полученного значения или
    - **Min \.\.\. Max** \(если Auto\-scaling выключен\) – фиксированный диапазон отображения данных
    - **Position** \- размещение оси данных: слева или справа от графика
    - **Make marks by** – засечки на графике, с указанным целочисленным интервалом
    - **Divisions between marks** – дополнительных пунктов между основными засечками
- **Список кривых** , которые отображает график, и их настройки 

    - **Name** – название кривой, можно отобразить на оси
    - **Tag** – переменная сервера, из которой график получает данные для построения кривой
    - **Main curve** \(for Auto\-scaling\) – отметить кривую как "главную" для авто\-масштабирования
    - **Line type** – тип кривой 

        - *Line* – точки кривой соединяются отрезками прямой, линия непрерывная
        - *Dotted line* – точки кривой соединяются отрезками прямой, линия пунктирная
        - *Square line* – кривая строится ступеньками от точки до точки, линия непрерывная
    - **Width** – толщина линии или точки
    - **Color** – цвет линии

**Настройки области диаграммы** \(Appearance\): 

- Заливка в области диаграммы и области осей
- Горизонтальная ось \(время\): линия, засечки, дополнительные засечки, текст на засечках, заголовок оси
- Вертикальная ось \(данные\): линия, засечки, дополнительные засечки, текст на засечках, заголовок оси
- Курсор в области диаграммы

**Пример:** 

:::tip
**:::warning
 скачать: 
:::** [настройка графиков для i3 pro и сохранения базы для iRidium server ](http://iridiumdeveloperdoc.s3.amazonaws.com/JS%20sampleas%20and%20docs/Server/trends.rar)

:::

![123](/img/Графики_и_диаграммы/Trend1.png)

![123](/img/Графики_и_диаграммы/Trend2.png)

![123](/img/Графики_и_диаграммы/Trend3.png)

###  Заполнение графика массивом данных из JavaScript 

Вы можете передать в кривую графика данные в виде двумерного массива, содержащего координаты точек кривой графика\. 

**Пример массива:** 

```javascript
var l_aArray = [[0, 60], [1, 30], [2, 90], [3, 10], [4, 60], [5, 20], [6, 80]];
```

**Пример реализации:** 

```javascript
function trend_processer(trend, curve_name) {
    var trend_curve = trend.GetCurve(curve_name);
    trend_curve.SetCurveTag("");    
    trend.EndTime = new iDate();
 
    this.Show = function (data_array) {
        trend_curve.SetData(data_array, 0, data_array.length - 1);
    }
}
 
// get a curve
var Curve1 = new trend_processer(IR.GetPage("Page 1").GetItem("Item 1"), 
            "Main curve");
 
// display data
Curve1.Show([[0, 60], [1, 30], [2, 90], [3, 10], [4, 60], [5, 20], [6, 80]]);
```

**Результирующая кривая:** 

![123](/img/Графики_и_диаграммы/Studio2019_Trend_from_array.png)

![123](/img/Графики_и_диаграммы/Studio2019_Trend_from_array_curve.png)

###  Заполнение графика из внешней SQL базы данных 

Чтобы вывести информацию из внешней базы данны: 

1. настройте [драйвер ODBC ](https://dev.iridi.com/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%9C%D0%BE%D0%B9_%D1%8F%D0%B7%D1%8B%D0%BA/ODBC)в проекте для iRidium server, добавьте скрипт **\#1**
1. создайте виртуальный тег, через который данные будут передаваться с серверного проекта в панельный
1. создайте интерфейс для i3 pro, добавьте в него элемент Linear Trend для отображения данных и скрипт **\#2**

**скрипт \#1 для iRidium server:** 

```javascript
IR.AddListener(IR.EVENT_START,0,function()
{  
IR.SetTimeout(2000, function(){
   var MySQL = new ODBC("root", "", "MySQLresurs"); // creating database connection object
   if(MySQL == false)
   {
      IR.Log("Wrong connection");
   }
   else
   {
      IR.Log("Right connection");
   }
   var response = MySQL.Query("SELECT * FROM test");
   if (response)          // if connection is successful and answer exists
   {
       var rows = response.GetRows();
       var columns = response.GetColumns();
       var data = {};               // two-dimension array with query result
       for (var i = 0; i < columns; i++) {
           var colName = response.GetColumnName(i);
           data[colName] = [];
           for (var j = 0; j < rows; j++) {
               data[colName][j] = response.GetRowValue(i, j);
           }
       }
    response.Free(); // free memory of recordset (optional action for memory optimization)
    IR.Log(JSON.Stringify(data));
    IR.SetVariable("Server.Tags.Data",JSON.Stringify(data));
    }
});
});
```

**скрипт \#2 для i3 pro:** 

```javascript
var l_oDevice = IR.GetDevice("iRidium Server");
var l_oPage = IR.GetPage("Page 1");
var l_oTrend = l_oPage.GetItem("Item 1");
var L_oCurve = l_oTrend.GetCurve("test"); 
var l_aArray = [];
 
IR.AddListener(IR.EVENT_TAG_CHANGE, l_oDevice ,function(m_sTag, m_sData) {
   if(m_sTag == "Data"){
      l_aArray = [];
      var m_oData = JSON.Parse(m_sData);
      for(var Index in m_oData["X"]){
         l_aArray[Index] = [m_oData["X"][Index], m_oData["Y"][Index]+0];    
      }
   }
});
```

:::tip
**:::warning
 скачать: 
:::

[пример получения данных через драйвер ODBC ](https://s3.amazonaws.com/iRidiumWiki2.0/iRidiumGUIEditor/Samples/Trends.rar)** 

:::

###  Настройка графика с помощью JavaScript 

Как и любой другой элемент Linear Trend имеет свои параметры, к которым можно обращаться непосредственно через скрипты\. Опишем сценарий, который будет выводить время начала работы \(StartTime\) графика в лог: 

```javascript
var trend = IR.GetPage("Page 1").GetItem("Item 1"); // Получаем указатель на график.
IR.Log("Trend start:"+trend.StartTime); // Выводим время начала работы тренда в виде десятичного числа.
var date = new iDate(trend.StartTime); // Осуществляем перевод числа в формат даты.
IR.Log("Year = " + date.year);
IR.Log("Month = " + date.month);
IR.Log("Date = " + date.date);
IR.Log("Hours = " + date.hours);
IR.Log("Minutes = " + date.minutes);
IR.Log("Seconds = " + date.seconds);
```

Сценарий выводит диапазон \(Range\) графика в лог: 

```javascript
date = new iDate(trend.Range);
IR.Log("RANGE = "+date.minutes);
```

Если вы хотите изменить диапазон, т\.е\. изменить шкалу ОХ, вам необходимо изменить значение параметра Range: 

```javascript
trend.Range = 0.00138889; //Для Range число 1 = 1 дню, значит 1 час = 1/24 и т.д.
```

Разберём изменение настроек шкалы OY\. Чтобы изменить эти настройки, нам необходимо знать имя нужного нам графика: 

1. Зайдите в настройки тренда,
1. Перейдите во вкладку General,
1. Выберите нужный вам график\.

![123](/img/Графики_и_диаграммы/Trend5.png)

```javascript
var graph= trend.GetCurve("Feedback 1"); //Получаем указатель на нужный график
//Выводим в лог информацию о графике: 
IR.Log("Curve min:" + graph.Min); // Минимальное значение шкалы OY
IR.Log("Curve max:" +graph.Max); // Максимальное значение шкалы OY
IR.Log("Curve color:" +graph.Color); // Цвет графика
```

Изменим эти параметры: 

```javascript
graph.Min = 0;
graph.Max = 75;
graph.Color = 0x00FF00FF; //Обратите внимание на шаблон изменения цвета: 0x - перевод из системы счисления HEX в DEС, первые 6 символов - цветовая палитра RGB, последние два - прозрачность (FF - непрозрачный, 00 - полностью прозрачный)
```

Для просмотра истории изменения параметров фидбека можно использовать функцию перемотки тренда\. Данная функция помогает отследить изменения не переключая режим тренда\. 

```javascript
function left() {
    trend.Stop; // Происходит остановка тренда
    trend.StartTime = trend.StartTime-1/720; // перемещение относительно шкалы ОХ на определённое время назад
    trend.EndTime = trend.EndTime-1/720; // 1/720 - смещение времени на две минуты
};
 
function right() {
    trend.Stop; // Происходит остановка тренда
    trend.StartTime = trend.StartTime+1/720; // Смещение шкалы ОХ на определённое время вперёд
    trend.EndTime = trend.EndTime+1/720;
};
```

Более подробное описание свойств и методов работы с графиком [здесь ](https://dev.iridi.com/Trends)\. 

##  Круговые и столбцовые диаграммы 

Диаграммы – способ визуального сопоставления нескольких значений в интерфейсе визуализации\. Они используют текущие значения переменных, а не исторические данные, поэтому работают и без iRidium server\. 

###  Круговая диаграмма \(Pie Chart\) 

**Pie Chart** \(круговая диаграмма\) – разделена на фрагменты\-секторы для иллюстрации числовой пропорции\. На круговой диаграмме длина дуги каждого среза пропорциональна величине, которую он представляет\. 

![123](/img/Графики_и_диаграммы/PieChart2.png)

| Type | Pie Chart |
| --- | --- |
| SectorGap | Промежуток между секторами\. |
| ConvasColor | Цвет фона элемента, на котором располагается диаграмма\. |
| ConvasOpacity | Непрозрачность фона элемента от 0 до 255\. |
| BorderColor | Рамка фоновой части элемента\. |
| BorderDepth | Ширина рамки фоновой части элемента\. |
| ChartSectors | Добавление и настройка секторов круговой диаграммы\. :::info Настройка диаграммы производится с помощью ::: [скриптов ](https://dev.iridi.com#Настройка_диаграммы_с_помощью_скриптов)или [заполнением параметров ](https://dev.iridi.com#Настройка_диаграммы_в_iRidium_Studio)в iRidium Studio\. |

####  Настройка диаграммы в iRidium Studio 

![123](/img/Графики_и_диаграммы/PieChart1.png)

`1` Откройте окно настройки круговой диаграммы двойным кликом по элементу или с помощью параметра элемента **ChartSectors** на динамической панели\. 

`2` Нажмите "\+" для добавления сектора круговой диаграммы\. 

`3` Задайте параметры каждому сектору круговой диаграммы: 

- **Name** \- имя сектора,
- **Token** \- токен, значение которого будет отображено на круговой диаграмме,
- **Color** \- цвет сектора\.

**Пример:** 

:::tip
**:::warning
 скачать: 
:::** [настройка элемента Pie Chart в iRidium Studio\. ](https://s3.amazonaws.com/iRidiumWiki2.0/PieChart/Pie+Chart.irpz)

:::

####  Настройка диаграммы с помощью скриптов 

В диаграмму передается массив объектов \- секторов диаграммы, у которых есть ключи Value \(значение, целое число\) и Color \(цвет, HEX код\)\. Значением и цветом можно управлять в процессе работы клиента, передавая объекту массива новые значения\. Можно менять количество секторов, добавляя и удаляя элементы массива\. 

**Пример \#1** заполнения диаграммы: 

```javascript
   var chart = IR.GetItem("PiePage").GetItem("pie");
 
   chart.Data = [
      {
        Value: 20,
        Color: 0xF7464AFF,
      },
      {
        Value: 45,
        Color: 0x46BFBDFF,
      },
      {
        Value: 100,
        Color: 0xFDB45CFF,
      }
   ];
```

**Пример \#2** заполнения диаграммы данными из разных источников: 

```javascript
// add a new Pie
var Pie_1 = new pie_processer(IR.GetItem("PiePage").GetItem("pie"));
 
// add a constant as piece of Pie
Pie_1.AddPiece("Orange", 0xFDB45CFF, 30);
 
// remove one of piecs
Pie_1.RemovePiece("Orange");
 
// change a pice on the level release
IR.AddListener(IR.EVENT_ITEM_RELEASE, IR.GetItem("PiePage").GetItem("level_1"), function() {
  var value = IR.GetItem("PiePage").GetItem("level_1").Value;  
  Pie_1.AddPiece("Red", 0xF7464AFF, value);
});
 
// one more piece that displayed on "tag change" of Driver
IR.AddListener(IR.EVENT_TAG_CHANGE, IR.GetDevice("KNX"), function(name,value) {
  if (name = "1/1/1") {
      Pie_1.AddPiece("Green", 0x2EFF0AFF, value);
  }
});
 
 
// processing of added PieCharts
function pie_processer(chart) {
   var piece = {};
 
   this.AddPiece = function (in_name, in_color, in_value) {
       piece[in_name] = {Color: in_color, Value: in_value};
       update_pie();
   };
 
   this.RemovePiece = function (in_name) {
       delete piece[in_name];
       update_pie();
   };
 
   function update_pie() {
      var data = [];
      for (key in piece) {
          data.push(piece[key]);
      } 
      chart.Data = data;  
  };                   
}
```

###  Столбцовая диаграмма \(Bar Chart\) 

**Bar Chart** \(столбцовая диаграмма\) – отображает сравнение нескольких значений, представленных прямоугольными зонами, высоты \(длины\) которых пропорциональны величинам, которые они отображают\. Заполнение диаграммы производится из скриптов\. 

Заполнение диаграммы производится из скриптов\. В диаграмму передается массив объектов \- секторов диаграммы, у которых есть ключи Value \(значение, целое число\) и Color \(цвет, HEX код\)\. Значением и цветом можно управлять в процессе работы клиента, передавая объекту массива новые значения\. Можно менять количество секторов, добавляя и удаляя элементы массива\. 

**Пример \#1** заполнения диаграммы: 

```javascript
IR.AddListener(IR.EVENT_START, 0, function () {
 
    var chart1 = IR.GetItem("BarPage").GetItem("bar1");
 
    chart1.Data = {
            Labels : ["Value"], // text on the horizontal axis
            Datasets : [{
                FillColor : 0x0099CC80, // column color
                StrokeColor : 0xFF0004FF, // column border color
                Data : [100] // var value
            }, {
                FillColor : 0x9933CC80,
                StrokeColor : 0x00FF33FF,
                Data : [100]
            }, {
                FillColor : 0xFF33CC80,
                StrokeColor : 0xFF33CCFF,
                Data : [100]
            }]
    }
 
    chart1.ChartType = 1; // column / stack / square
    chart1.StrokeWidth = 3; // the width of a single column
    chart1.BarGap = 1; // the distance between columns
    chart1.SetGap = 8;
    chart1.GridColor = 0xFF0000FF; // the color of greed
    chart1.GridStep = 25; // the distance between greed lines
    chart1.ShiftX = 10; // the diatance betweeenhorizontal axis and columns
    chart1.TextColor = 0xFF0000FF; // the color of labels and greed numbers
});
```

NewPP limit report
CPU time usage: 0\.137 seconds
Real time usage: 0\.192 seconds
Preprocessor visited node count: 316/1000000
Preprocessor generated node count: 752/1000000
Post‐expand include size: 1171/2097152 bytes
Template argument size: 395/2097152 bytes
Highest expansion depth: 3/40
Expensive parser function count: 0/100 Saved in parser cache with key irmob\_wiki3:pcache:idhash:29833\-0\!\*\!0\!\!ru\!5\!\* and timestamp 20250712110835 and revision id 134687