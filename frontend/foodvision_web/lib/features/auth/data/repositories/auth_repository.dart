import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../../core/network/api_client.dart';
import '../models/auth_tokens_model.dart';
import '../models/user_model.dart';

class AuthRepository {
  final Dio _dio;
  final SharedPreferences _prefs;

  static const String _accessTokenKey = 'foodvision_access_token';
  static const String _refreshTokenKey = 'foodvision_refresh_token';

  AuthRepository(ApiClient apiClient, SharedPreferences prefs)
      : _dio = apiClient.dio,
        _prefs = prefs;

  String? get accessToken => _prefs.getString(_accessTokenKey);
  String? get refreshToken => _prefs.getString(_refreshTokenKey);
  bool get isAuthenticated => accessToken != null;

  Future<void> _saveTokens(AuthTokensModel tokens) async {
    await _prefs.setString(_accessTokenKey, tokens.accessToken);
    await _prefs.setString(_refreshTokenKey, tokens.refreshToken);
  }

  Future<void> _clearTokens() async {
    await _prefs.remove(_accessTokenKey);
    await _prefs.remove(_refreshTokenKey);
  }

  /// Registers a new user account.
  Future<UserModel> register({
    required String email,
    required String password,
  }) async {
    final response = await _dio.post(
      '/api/v1/auth/register',
      data: {'email': email.trim(), 'password': password},
    );
    return UserModel.fromJson(Map<String, dynamic>.from(response.data as Map));
  }

  /// Logs in and persists the JWT access/refresh token pair.
  Future<AuthTokensModel> login({
    required String email,
    required String password,
  }) async {
    final response = await _dio.post(
      '/api/v1/auth/login',
      data: {'email': email.trim(), 'password': password},
    );

    final tokens = AuthTokensModel.fromJson(
      Map<String, dynamic>.from(response.data as Map),
    );
    await _saveTokens(tokens);
    return tokens;
  }

  /// Fetches the profile of the currently authenticated user.
  Future<UserModel> getCurrentUser() async {
    final token = accessToken;
    if (token == null) {
      throw Exception('Not authenticated');
    }

    final response = await _dio.get(
      '/api/v1/auth/me',
      options: Options(headers: {'Authorization': 'Bearer $token'}),
    );
    return UserModel.fromJson(Map<String, dynamic>.from(response.data as Map));
  }

  /// Logs out the user and revokes the refresh token on the server.
  Future<void> logout() async {
    final token = refreshToken;
    if (token != null) {
      try {
        await _dio.post(
          '/api/v1/auth/logout',
          data: {'refresh_token': token},
        );
      } catch (_) {
        // Fallback silently if server is unreachable during logout
      }
    }
    await _clearTokens();
  }
}