import 'package:bloc_test/bloc_test.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:foodvision_web/features/auth/cubit/auth_cubit.dart';
import 'package:foodvision_web/features/auth/cubit/auth_state.dart';
import 'package:foodvision_web/features/auth/data/models/auth_tokens_model.dart';
import 'package:foodvision_web/features/auth/data/models/user_model.dart';
import 'package:foodvision_web/features/auth/data/repositories/auth_repository.dart';
import 'package:mocktail/mocktail.dart';

class MockAuthRepository extends Mock implements AuthRepository {}

void main() {
  late MockAuthRepository repository;

  setUp(() {
    repository = MockAuthRepository();
  });

  final fakeUser = UserModel(
    id: 'user-123',
    email: 'test@example.com',
    role: 'user',
    isActive: true,
    createdAt: DateTime.parse('2026-01-01T00:00:00Z'),
  );

  const fakeTokens = AuthTokensModel(
    accessToken: 'fake-access',
    refreshToken: 'fake-refresh',
  );

  group('AuthCubit Tests', () {
    blocTest<AuthCubit, AuthState>(
      'checkAuthStatus emits Unauthenticated when no token saved',
      build: () {
        when(() => repository.isAuthenticated).thenReturn(false);
        return AuthCubit(repository);
      },
      act: (cubit) => cubit.checkAuthStatus(),
      expect: () => [
        const Unauthenticated(),
      ],
    );

    blocTest<AuthCubit, AuthState>(
      'checkAuthStatus emits Authenticated when token valid and user fetched',
      build: () {
        when(() => repository.isAuthenticated).thenReturn(true);
        when(() => repository.getCurrentUser()).thenAnswer((_) async => fakeUser);
        return AuthCubit(repository);
      },
      act: (cubit) => cubit.checkAuthStatus(),
      expect: () => [
        const AuthLoading(),
        Authenticated(fakeUser),
      ],
    );

    blocTest<AuthCubit, AuthState>(
      'login emits Loading and Authenticated on valid credentials',
      build: () {
        when(() => repository.login(email: 'test@example.com', password: 'password123'))
            .thenAnswer((_) async => fakeTokens);
        when(() => repository.getCurrentUser()).thenAnswer((_) async => fakeUser);
        return AuthCubit(repository);
      },
      act: (cubit) => cubit.login(email: 'test@example.com', password: 'password123'),
      expect: () => [
        const AuthLoading(),
        Authenticated(fakeUser),
      ],
    );

    blocTest<AuthCubit, AuthState>(
      'login emits AuthError when credentials invalid',
      build: () {
        when(() => repository.login(email: 'test@example.com', password: 'wrong'))
            .thenThrow(DioException(
          requestOptions: RequestOptions(path: '/api/v1/auth/login'),
          response: Response(
            requestOptions: RequestOptions(path: '/api/v1/auth/login'),
            statusCode: 401,
            data: {'detail': 'Incorrect email or password'},
          ),
        ));
        return AuthCubit(repository);
      },
      act: (cubit) => cubit.login(email: 'test@example.com', password: 'wrong'),
      expect: () => [
        const AuthLoading(),
        const AuthError('Incorrect email or password'),
      ],
    );

    blocTest<AuthCubit, AuthState>(
      'logout emits Loading then Unauthenticated',
      build: () {
        when(() => repository.logout()).thenAnswer((_) async {});
        return AuthCubit(repository);
      },
      act: (cubit) => cubit.logout(),
      expect: () => [
        const AuthLoading(),
        const Unauthenticated(),
      ],
    );
  });
}