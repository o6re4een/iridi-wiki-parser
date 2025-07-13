# Инструменты отладки i3 pro и iRidium server

##  Способы отладки 

**На Windows:** 

- когда приложение **i3 pro** запущено на ПК с Windows, окно лога можно открыть по нажатию **F4**
- **iRidium server** на Windows \- это консоль, в которой вы видите сообщения лога\.

Телефоны и планшеты на базе Android поддерживают [отладку по USB ](https://dev.iridi.com/Android_USB_Debugging)\. 

**В аппаратных реализациях  iRidium server** необходимо подключиться к серверу для просмотра лога: 

- к **UMC** и другим устройствам можно [подключиться через консоль ](https://dev.iridi.com/IRidium_Server_UMC_C3#Получение_доступа_через_консоль)
- архив логов можно открыть через [web\-интерфейс ](https://dev.iridi.com/Web_interface#Archive_Logs)сервера на любой платформе
- с любого устройства можно переслать лог на ПК по протоколу SMTP\. Для этого на ПК устанавливается SMTP сервер, который принимает лог, а в iRidium studio выполняется настройка связи с SMTP сервером

##  Настройка в iRidium studio 

**Данные в лог** записывают 

1. **драйверы** , которые вы добавили в проект
1. i3 pro при запуске и в процессе работы \(сообщения о работе системы, общие данные\)
1. **скрипты** , для этого есть метод [IR\.Log\(\) ](https://dev.iridi.com/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%9C%D0%BE%D0%B9_%D1%8F%D0%B7%D1%8B%D0%BA/Systems_API#IR.Log)\. Также скрипты записывают в лог сообщения об ошибках

**Количество сообщений от драйвера** зависит от детализации лога \(Debug level\), которую можно настроить в параметрах каждого драйвера отдельно: 

![123](/img/Способы_отладки/Studio2019_Drivers_DebugLevel.png)

**Отладка через SMTP сервер** и количество сообщений для отправки можно регулировать в настройках интерфейса, вкладка **Debug** : 

![123](/img/Способы_отладки/Studio2019_Drivers_DebugLevel_SMTP.png)

NewPP limit report
CPU time usage: 0\.030 seconds
Real time usage: 0\.034 seconds
Preprocessor visited node count: 52/1000000
Preprocessor generated node count: 172/1000000
Post‐expand include size: 537/2097152 bytes
Template argument size: 255/2097152 bytes
Highest expansion depth: 3/40
Expensive parser function count: 0/100 Saved in parser cache with key irmob\_wiki3:pcache:idhash:29825\-0\!\*\!0\!\!\*\!5\!\* and timestamp 20250712133418 and revision id 77680