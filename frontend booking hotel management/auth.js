/**
 * Auth Module — Login & Registration
 */

const Auth = (() => {
  function renderLogin() {
    document.getElementById('auth-container').innerHTML = `
      <div class="auth-page">
        <div class="auth-brand">
          <div class="brand-logo">Aurum<br>Hotel</div>
          <div class="brand-tagline">Management Suite</div>
          <ul class="brand-features">
            <li>Manage bookings &amp; reservations</li>
            <li>Track rooms, guests &amp; services</li>
            <li>Process payments in real time</li>
            <li>Monitor staff &amp; performance</li>
          </ul>
        </div>
        <div class="auth-form-side">
          <div class="auth-card">
            <h1 class="auth-title">Welcome back</h1>
            <p class="auth-subtitle">Sign in to your account to continue</p>
            <form id="login-form" novalidate>
              <div class="form-group">
                <label class="form-label" for="login-username">Username <span class="required">*</span></label>
                <input class="form-control" type="text" id="login-username" name="username" placeholder="your username" autocomplete="username">
                <div class="form-error" id="login-username-err"></div>
              </div>
              <div class="form-group">
                <label class="form-label" for="login-password">Password <span class="required">*</span></label>
                <input class="form-control" type="password" id="login-password" name="password" placeholder="••••••••" autocomplete="current-password">
                <div class="form-error" id="login-password-err"></div>
              </div>
              <div class="form-error" id="login-global-err" style="margin-bottom:0.75rem;font-size:0.85rem;"></div>
              <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;padding:0.65rem;" id="login-btn">
                Sign In
              </button>
            </form>
            <p class="auth-switch">Don't have an account? <a href="#" id="go-register">Create one</a></p>
          </div>
        </div>
      </div>`;

    const schema = {
      'login-username': [Validate.rules.required],
      'login-password': [Validate.rules.required],
    };
    Validate.attachLiveValidation(schema);

    document.getElementById('go-register').addEventListener('click', (e) => {
      e.preventDefault();
      renderRegister();
    });

    document.getElementById('login-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const errGlobal = document.getElementById('login-global-err');
      errGlobal.classList.remove('visible');

      if (!Validate.validateForm(schema)) return;

      const btn = document.getElementById('login-btn');
      setLoading(btn, true);

      try {
        const res = await API.auth.login(
          document.getElementById('login-username').value,
          document.getElementById('login-password').value
        );
        API.setToken(res.access_token);
        const me = await API.auth.me();
        App.init(me);
      } catch (err) {
        errGlobal.textContent = err.message || 'Login failed. Check your credentials.';
        errGlobal.classList.add('visible');
      } finally {
        setLoading(btn, false);
      }
    });
  }

  function renderRegister() {
    document.getElementById('auth-container').innerHTML = `
      <div class="auth-page">
        <div class="auth-brand">
          <div class="brand-logo">Aurum<br>Hotel</div>
          <div class="brand-tagline">Management Suite</div>
          <ul class="brand-features">
            <li>Manage bookings &amp; reservations</li>
            <li>Track rooms, guests &amp; services</li>
            <li>Process payments in real time</li>
            <li>Monitor staff &amp; performance</li>
          </ul>
        </div>
        <div class="auth-form-side">
          <div class="auth-card">
            <h1 class="auth-title">Create account</h1>
            <p class="auth-subtitle">Register to access the management suite</p>
            <form id="register-form" novalidate>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label" for="reg-username">Username <span class="required">*</span></label>
                  <input class="form-control" type="text" id="reg-username" name="username" placeholder="username">
                  <div class="form-error" id="reg-username-err"></div>
                </div>
                <div class="form-group">
                  <label class="form-label" for="reg-email">Email <span class="required">*</span></label>
                  <input class="form-control" type="email" id="reg-email" name="email" placeholder="you@example.com">
                  <div class="form-error" id="reg-email-err"></div>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label" for="reg-full-name">Full Name <span class="required">*</span></label>
                <input class="form-control" type="text" id="reg-full-name" name="full_name" placeholder="John Smith">
                <div class="form-error" id="reg-full-name-err"></div>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label" for="reg-password">Password <span class="required">*</span></label>
                  <input class="form-control" type="password" id="reg-password" name="password" placeholder="••••••••">
                  <div class="form-error" id="reg-password-err"></div>
                </div>
                <div class="form-group">
                  <label class="form-label" for="reg-confirm">Confirm <span class="required">*</span></label>
                  <input class="form-control" type="password" id="reg-confirm" name="confirm" placeholder="••••••••">
                  <div class="form-error" id="reg-confirm-err"></div>
                </div>
              </div>
              <div class="form-error" id="reg-global-err" style="margin-bottom:0.75rem;font-size:0.85rem;"></div>
              <button type="submit" class="btn btn-primary" style="width:100%;justify-content:center;padding:0.65rem;" id="reg-btn">
                Create Account
              </button>
            </form>
            <p class="auth-switch">Already have an account? <a href="#" id="go-login">Sign in</a></p>
          </div>
        </div>
      </div>`;

    const schema = {
      'reg-username':  [Validate.rules.required, Validate.rules.minLen(3)],
      'reg-email':     [Validate.rules.required, Validate.rules.email],
      'reg-full-name': [Validate.rules.required],
      'reg-password':  [Validate.rules.required, Validate.rules.minLen(6)],
      'reg-confirm': [
        Validate.rules.required,
        (v) => v === document.getElementById('reg-password').value ? null : 'Passwords do not match.',
      ],
    };
    Validate.attachLiveValidation(schema);

    document.getElementById('go-login').addEventListener('click', (e) => {
      e.preventDefault();
      renderLogin();
    });

    document.getElementById('register-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const errGlobal = document.getElementById('reg-global-err');
      errGlobal.classList.remove('visible');

      if (!Validate.validateForm(schema)) return;

      const btn = document.getElementById('reg-btn');
      setLoading(btn, true);

      try {
        await API.auth.register({
          username:  document.getElementById('reg-username').value,
          email:     document.getElementById('reg-email').value,
          full_name: document.getElementById('reg-full-name').value,
          password:  document.getElementById('reg-password').value,
        });
        Toast.success('Account created! Please sign in.');
        renderLogin();
      } catch (err) {
        errGlobal.textContent = err.message || 'Registration failed.';
        errGlobal.classList.add('visible');
      } finally {
        setLoading(btn, false);
      }
    });
  }

  return { renderLogin, renderRegister };
})();
