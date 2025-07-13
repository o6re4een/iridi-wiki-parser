---
id: IRidium_studio_2019_UI_Relations
title: Relations связи внутри интерфейса i3 pro
---
# Relations: связи внутри интерфейса i3 pro

Связи \- это способ изменить свойство графического элемента при изменении фидбека оборудования, токена или свойства другого элемента\. Связи очень широко используются в интерфейсе визуализации: посмотреть, в каких связях участвует конкретный элемент, можно в панели PROGRAMMING \> Relations\. 

Связь состоит из ссылки на приемник данных и ссылки на источник данных\. Значение источника присваивается приемнику как есть, без изменений: 

![123](/img/IRidium_studio_2019_UI_Relations/Studio2019_Drivers_Relations_Structure.png)

**Пример:** текстовое поле элемента принимает значение из токена системы, содержащего текущую дату\. При каждом изменении даты, изменится и значение в текстовом поле: 

![123](/img/IRidium_studio_2019_UI_Relations/Studio2019_Drivers_Relations_Sample.png)

- Project token \- переменная проекта
- System token \- переменная с информацией о системе
- Page, Popup, Item \- свойство элемента интерфейса
- Feedback \- канал обратной связи, возвращающий значение от оборудования
- Driver token \- переменная драйвера
- Module tag \- канал обратной связи, возвращающий значение от [lite\-модуля ](https://dev.iridi.com/IRidium_studio_2019_Ready_Solutions#Lite_модули-виджеты)

Связь может не затрагивать графический элемент: например, записывать данные из системного токена в токен проекта\. Такие ситуации редки, но возможны\. Особенность их состоит в том, что не будет графического элемента, в свойствах которого можно увидеть такую связь\. На этот случай используйте окно **Relations** , отображающее все созданные связи\. В нем можно не только увидеть связи, но и создать новую: 

![123](/img/IRidium_studio_2019_UI_Relations/Studio2019_Drivers_Relations_AllRelationsWindow.png)

NewPP limit report
CPU time usage: 0\.023 seconds
Real time usage: 0\.025 seconds
Preprocessor visited node count: 22/1000000
Preprocessor generated node count: 82/1000000
Post‐expand include size: 390/2097152 bytes
Template argument size: 216/2097152 bytes
Highest expansion depth: 2/40
Expensive parser function count: 0/100 Saved in parser cache with key irmob\_wiki3:pcache:idhash:29816\-0\!\*\!0\!\*\!\*\!5\!\* and timestamp 20250713085001 and revision id 77656