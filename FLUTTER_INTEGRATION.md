# 🚀 Flutter Integration Guide

## API Base URL
```
https://web-production-cd82d9.up.railway.app
```

## 📋 Доступные эндпоинты

### 🔐 Авторизация

#### 1. Регистрация пользователя
**POST** `/api/auth/register`

**Request Body:**
```json
{
  "username": "myusername",
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "message": "User created successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "myusername",
    "email": "user@example.com"
  }
}
```

#### 2. Логин
**POST** `/api/auth/login`

**Request Body:**
```json
{
  "username": "myusername",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "myusername",
    "email": "user@example.com"
  }
}
```

#### 3. Получить текущего пользователя
**GET** `/api/auth/me`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "id": 1,
  "username": "myusername",
  "email": "user@example.com",
  "created_at": "2026-06-20T08:00:00.000000"
}
```

---

### 🏢 Объекты недвижимости (CRUD)

#### 1. Получить все объекты пользователя
**GET** `/api/objects`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "address": "Moscow, Arbat 10",
    "area": 75.5,
    "is_for_sale": true,
    "price_total": 15000000,
    "rent_per_sqm": 1500,
    "profitability": 6.5,
    "is_undervalued": true,
    "created_at": "2026-06-20T08:00:00.000000",
    "updated_at": "2026-06-20T08:00:00.000000"
  }
]
```

#### 2. Создать новый объект
**POST** `/api/objects`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "address": "Moscow, Arbat 10",
  "area": 75.5,
  "is_for_sale": true,
  "price_total": 15000000,
  "rent_per_sqm": 1500,
  "profitability": 6.5,
  "is_undervalued": true
}
```

**Response (201):**
```json
{
  "message": "Object created successfully",
  "object": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "address": "Moscow, Arbat 10",
    "area": 75.5,
    "is_for_sale": true,
    "price_total": 15000000,
    "rent_per_sqm": 1500,
    "profitability": 6.5,
    "is_undervalued": true
  }
}
```

#### 3. Получить объект по ID
**GET** `/api/objects/{object_id}`

**Headers:**
```
Authorization: Bearer {access_token}
```

#### 4. Обновить объект
**PUT** `/api/objects/{object_id}`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "address": "Updated address",
  "profitability": 7.2
}
```

#### 5. Удалить объект
**DELETE** `/api/objects/{object_id}`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "message": "Object deleted successfully"
}
```

---

### 📊 Аналитика

#### Получить сводку по объектам
**GET** `/api/analytics/summary`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "count": 10,
  "avg_profitability": 6.75,
  "undervalued_count": 3,
  "for_sale_count": 5,
  "for_rent_count": 5
}
```

---

## 📱 Пример Flutter кода

### 1. Добавить зависимости в `pubspec.yaml`

```yaml
dependencies:
  http: ^1.1.0
  shared_preferences: ^2.2.2
```

### 2. Создать API Service

```dart
// lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'https://web-production-cd82d9.up.railway.app';
  String? _token;

  Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('access_token');
  }

  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
    _token = token;
  }

  Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    _token = null;
  }

  // Регистрация
  Future<Map<String, dynamic>> register(String username, String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 201) {
      final data = jsonDecode(response.body);
      await saveToken(data['access_token']);
      return data;
    } else {
      throw Exception('Registration failed: ${response.body}');
    }
  }

  // Логин
  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await saveToken(data['access_token']);
      return data;
    } else {
      throw Exception('Login failed: ${response.body}');
    }
  }

  // Получить объекты
  Future<List<dynamic>> getObjects() async {
    await loadToken();
    if (_token == null) throw Exception('Not authenticated');

    final response = await http.get(
      Uri.parse('$baseUrl/api/objects'),
      headers: {
        'Authorization': 'Bearer $_token',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load objects: ${response.body}');
    }
  }

  // Создать объект
  Future<Map<String, dynamic>> createObject(Map<String, dynamic> objectData) async {
    await loadToken();
    if (_token == null) throw Exception('Not authenticated');

    final response = await http.post(
      Uri.parse('$baseUrl/api/objects'),
      headers: {
        'Authorization': 'Bearer $_token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(objectData),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to create object: ${response.body}');
    }
  }

  // Получить аналитику
  Future<Map<String, dynamic>> getAnalytics() async {
    await loadToken();
    if (_token == null) throw Exception('Not authenticated');

    final response = await http.get(
      Uri.parse('$baseUrl/api/analytics/summary'),
      headers: {
        'Authorization': 'Bearer $_token',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load analytics: ${response.body}');
    }
  }
}
```

### 3. Пример использования

```dart
// Инициализация сервиса
final apiService = ApiService();

// Регистрация
try {
  final result = await apiService.register(
    'testuser',
    'test@example.com',
    'password123',
  );
  print('Registered: ${result['user']['username']}');
} catch (e) {
  print('Error: $e');
}

// Логин
try {
  final result = await apiService.login('testuser', 'password123');
  print('Logged in: ${result['user']['username']}');
} catch (e) {
  print('Error: $e');
}

// Создать объект
try {
  final newObject = await apiService.createObject({
    'address': 'Moscow, Arbat 10',
    'area': 75.5,
    'is_for_sale': true,
    'price_total': 15000000,
    'rent_per_sqm': 1500,
    'profitability': 6.5,
    'is_undervalued': true,
  });
  print('Created object: ${newObject['object']['id']}');
} catch (e) {
  print('Error: $e');
}

// Получить все объекты
try {
  final objects = await apiService.getObjects();
  print('Total objects: ${objects.length}');
} catch (e) {
  print('Error: $e');
}

// Получить аналитику
try {
  final analytics = await apiService.getAnalytics();
  print('Total objects: ${analytics['count']}');
  print('Average profitability: ${analytics['avg_profitability']}%');
} catch (e) {
  print('Error: $e');
}
```

---

## ⚡ Быстрый старт

1. **Установить зависимости:**
   ```bash
   flutter pub get
   ```

2. **Скопировать файл `api_service.dart` в ваш проект**

3. **Инициализировать сервис:**
   ```dart
   final apiService = ApiService();
   ```

4. **Использовать методы API**

---

## 🔒 Безопасность

- Все эндпоинты (кроме `/api/health`, `/api/auth/register` и `/api/auth/login`) требуют JWT токен
- Токен передается в заголовке: `Authorization: Bearer {token}`
- Токен хранится в SharedPreferences
- Каждый пользователь видит только свои объекты

---

## 🌐 CORS настроен для Flutter Web

API настроен для работы с Flutter Web и поддерживает все необходимые CORS заголовки.

---

## 📝 Заметки

- Все даты возвращаются в формате ISO 8601
- ID объектов генерируются автоматически (UUID v4)
- Профитабельность (`profitability`) - это процент доходности
- `is_undervalued` - флаг недооцененного объекта
