import { UserManager, User } from 'oidc-client-ts';

const settings = {
  authority: import.meta.env.VITE_OIDC_AUTHORITY || 'https://accounts.google.com',
  client_id: import.meta.env.VITE_OIDC_CLIENT_ID || '',
  redirect_uri: `${window.location.origin}/callback`,
  response_type: 'code',
  scope: 'openid profile email',
  automaticSilentRenew: true,
  loadUserInfo: true
};

class AuthService {
  private userManager: UserManager;
  private user: User | null = null;

  constructor() {
    this.userManager = new UserManager(settings);
  }

  public async getUser(): Promise<User | null> {
    if (this.user) return this.user;
    this.user = await this.userManager.getUser();
    return this.user;
  }

  public async login(): Promise<void> {
    await this.userManager.signinRedirect();
  }

  public async completeLogin(): Promise<User> {
    this.user = await this.userManager.signinRedirectCallback();
    return this.user;
  }

  public async logout(): Promise<void> {
    await this.userManager.signoutRedirect();
  }

  public async isAuthenticated(): Promise<boolean> {
    const user = await this.getUser();
    return !!user && !user.expired;
  }
}

export const authService = new AuthService();