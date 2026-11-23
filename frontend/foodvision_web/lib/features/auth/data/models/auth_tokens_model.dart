import 'package:equatable/equatable.dart';

class AuthTokensModel extends Equatable {
  final String accessToken;
  final String refreshToken;
  final String tokenType;

  const AuthTokensModel({
    required this.accessToken,
    required this.refreshToken,
    this.tokenType = 'bearer',
  });

  factory AuthTokensModel.fromJson(Map<String, dynamic> json) {
    return AuthTokensModel(
      accessToken: json['access_token'] as String,
      refreshToken: json['refresh_token'] as String,
      tokenType: json['token_type'] as String? ?? 'bearer',
    );
  }

  Map<String, dynamic> toJson() => {
    'access_token': accessToken,
    'refresh_token': refreshToken,
    'token_type': tokenType,
  };

  @override
  List<Object?> get props => [accessToken, refreshToken, tokenType];
}