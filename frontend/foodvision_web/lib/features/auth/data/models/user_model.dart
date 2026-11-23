import 'package:equatable/equatable.dart';

class UserModel extends Equatable {
  final String id;
  final String email;
  final String role;
  final bool isActive;
  final DateTime createdAt;

  const UserModel({
    required this.id,
    required this.email,
    required this.role,
    required this.isActive,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as String,
      email: json['email'] as String,
      role: json['role'] as String? ?? 'user',
      isActive: json['is_active'] as bool? ?? true,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'email': email,
    'role': role,
    'is_active': isActive,
    'created_at': createdAt.toIso8601String(),
  };

  @override
  List<Object?> get props => [id, email, role, isActive, createdAt];
}