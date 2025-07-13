Image Eror**Поворот текста \(TextRotation\)** — это параметр, определяющий угол поворота текста внутри элемента в iRidi Studio и i3Pro\. Позволяет изменять ориентацию текста для улучшения читаемости или соответствия дизайну интерфейса\. 

Элементы, поддерживающие данный параметр: 

- Button
- Label
- Multistate Button
- Trigger Button
- Up/Down Button
- Level
- Multistate Level
- Circular Level
- Multistate Circular Level
- Joystick
- Virtual Key

Для остальных элементов данный параметр недоступен\. 

#  Доступные значения 

TextRotation принимает только фиксированные значения: 

- 0° — текст отображается в стандартном горизонтальном положении\.
- 90° — текст повёрнут по часовой стрелке на 90 градусов\.
- 180° — текст перевёрнут на 180 градусов\.
- 270° — текст повёрнут по часовой стрелке на 270 градусов\.

![123](/img/Text_transform/TextRotation01.png)

Не кратные 90 градусов значения \(например, 45°, 123°\) игнорируются\. 

При изменении TextRotation текст остается читаемым, но может измениться его положение относительно границ элемента\. 

#  Настройка TextRotation в iRidium Studio 

**1\. Через свойства элемента** 

- Выберите элемент\.
- В боковой панели PROJECT \> вкладка States, выберите TextRotation\.
- Установите одно из поддерживаемых значений \(0, 90, 180, 270\), нажмите Enter\.

![123](/img/Text_transform/TextRotation02.png)

**2\. Через быструю панель** 

- Выберите элемент\.
- Откройте редактор текста и измените TextRotation, нажмите Enter\. \.

![123](/img/Text_transform/TextRotation03.png)

#  Настройка TextRotation в Java Script 

TextRotation указывается следующим образом: 

TextRotation = доступные значения \(0, 90, 180, 270\) 

GetState = состояние элемента \(0 \- неактивное,1 \- активное\) 

```mw-content-ltr
IR.GetItem("Page 1").GetItem("Item 1").GetState(0).TextRotation = 270; // угол поворота текста

```

Попытка установить некорректное значение \(например, 45\) будет проигнорирована\. 

NewPP limit report
CPU time usage: 0\.069 seconds
Real time usage: 0\.078 seconds
Preprocessor visited node count: 50/1000000
Preprocessor generated node count: 178/1000000
Post‐expand include size: 236/2097152 bytes
Template argument size: 42/2097152 bytes
Highest expansion depth: 2/40
Expensive parser function count: 0/100 Saved in parser cache with key irmob\_wiki3:pcache:idhash:54090\-0\!\*\!\*\!\!ru\!5\!\* and timestamp 20250713183117 and revision id 147713