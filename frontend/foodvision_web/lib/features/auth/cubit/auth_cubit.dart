import 'package:dio/dio.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../data/repositories/auth_repository.dart';
import 'auth_state.dart';

class AuthCubit extends Cubit<AuthState> {
  final AuthRepository _repository;

  AuthCubit(this._repository) : super(const AuthInitial());

  /// Checks if an active session exists on app boot.
  Future<void> checkAuthStatus() async {
    if (!_repository.isAuthenticated) {
      emit(const Unauthenticated());
      return;
    }

    emit(const AuthLoading());
    try {
      final user = await _repository.getCurrentUser();
      emit(Authenticated(user));
    } catch (_) {
      await _repository.logout();
      emit(const Unauthenticated());
    }
  }

  /// Logs in a user, saves tokens, and loads their user profile.
  Future<void> login({
    required String email,
    required String password,
  }) async {
    emit(const AuthLoading());
    try {
      await _repository.login(email: email, password: password);
      final user = await _repository.getCurrentUser();
      emit(Authenticated(user));
    } on DioException catch (e) {
      final detail = e.response?.data is Map
          ? (e.response!.data as Map)['detail']?.toString()
          : null;
      emit(AuthError(detail ?? 'Invalid email or password.'));
    } catch (e) {
      emit(const AuthError('Unable to connect to authentication service.'));
    }
  }

  /// Registers a new user, automatically logs them in, and loads profile.
  Future<void> register({
    required String email,
    required String password,
  }) async {
    emit(const AuthLoading());
    try {
      await _repository.register(email: email, password: password);
      await _repository.login(email: email, password: password);
      final user = await _repository.getCurrentUser();
      emit(Authenticated(user));
    } on DioException catch (e) {
      final detail = e.response?.data is Map
          ? (e.response!.data as Map)['detail']?.toString()
          : null;
      emit(AuthError(detail ?? 'Registration failed. Email may already be in use.'));
    } catch (e) {
      emit(const AuthError('Unable to register at this time.'));
    }
  }

  /// Logs out the user and clears stored session.
  Future<void> logout() async {
    emit(const AuthLoading());
    await _repository.logout();
    emit(const Unauthenticated());
  }
}