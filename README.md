<table align="center">
  <tr>
    <td align="center" width="50%">
      <a href="https://laravel.com" target="_blank">
        <img src="https://raw.githubusercontent.com/laravel/art/master/logo-lockup/5%20SVG/2%20CMYK/1%20Full%20Color/laravel-logolockup-cmyk-red.svg" width="200" alt="Laravel Logo">
      </a>
      <br><br>
      <a href="https://github.com/laravel/framework/actions">
        <img src="https://github.com/laravel/framework/workflows/tests/badge.svg" alt="Build Status">
      </a>
      <a href="https://packagist.org/packages/laravel/framework">
        <img src="https://img.shields.io/packagist/v/laravel/framework" alt="Latest Stable Version">
      </a>
      <a href="https://packagist.org/packages/laravel/framework">
        <img src="https://img.shields.io/packagist/l/laravel/framework" alt="License">
      </a>
    </td>
    <td align="center" width="50%">
      <a href="https://vuejs.org/" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/9/95/Vue.js_Logo_2.svg" width="200" alt="Vue.js Logo">
      </a>
      <br><br>
      <img src="https://img.shields.io/badge/vuejs-%2335495e.svg?style=flat-square&logo=vuedotjs&logoColor=%234FC08D" alt="Vue.js Badge">
      <img src="https://img.shields.io/badge/vite-%23646CFF.svg?style=flat-square&logo=vite&logoColor=white" alt="Vite Badge">
      <img src="https://img.shields.io/badge/NPM-%23CB3837.svg?style=flat-square&logo=npm&logoColor=white" alt="NPM Badge">
    </td>
  </tr>
</table>

---

## 🛠️ Prerequisites & Setup

To ensure a smooth development experience with this Laravel + Vue.js project, please make sure your local environment is set up correctly.

### Essential Tools

| Tool | Description | Requirement / Link |
| :--- | :--- | :--- |
| <img src="https://www.php.net/images/logos/new-php-logo.svg" width="45"> | **PHP**<br>(Backend Runtime) | **Version 8.1+** is required.<br>[Download PHP](https://www.php.net/) |
| <img src="https://getcomposer.org/img/logo-composer-transparent.png" width="40"> | **Composer**<br>(PHP Dependency Manager) | Required to install Laravel packages.<br>[Download Composer](https://getcomposer.org/) |
| <img src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/nodejs/nodejs.png" width="35"> | **Node.js Runtime**<br>(Frontend Runtime) | **Version 18.0+ (LTS)** recommended.<br>[Download Node.js](https://nodejs.org/) |
| <img src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/npm/npm.png" width="35"> | **NPM**<br>(JS Package Manager) | Comes with Node.js. Used to compile Vue assets. |

### Recommended Extensions (VS Code)

| Tool | Description | Link |
| :--- | :--- | :--- |
| <img src="https://upload.wikimedia.org/wikipedia/commons/9/9a/Visual_Studio_Code_1.35_icon.svg" width="32"> | **VS Code** | The recommended editor.<br>[Download VS Code](https://code.visualstudio.com/) |
| <img src="https://vuejs.org/images/logo.png" width="32"> | **Vue - Official** | Syntax highlighting for Vue files.<br>[Extension Link](vscode:extension/Vue.volar) |
| <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Laravel.svg/1200px-Laravel.svg.png" width="30"> | **Laravel Blade Snippets** | Support for Blade templating.<br>[Extension Link](vscode:extension/onecentlin.laravel-blade) |

### Cara pemasangan

1. **Clone the repository**
   ```bash
   git clone https://github.com/Saha-hub123/FindServices.git
   ```
2. **Masuk kedalam foldernya**
   ```bash
   cd FindServices
   ```
3. **Install Backend Dependencies (Composer)**
   ```bash
   composer install
   ```
   > jangan lupa update jika sudah ada
   ```bash
   composer update
   ```
4. **Install Frontend Dependencies (NPM)**
   ```bash
   npm install vite@7 laravel-vite-plugin@2 @vitejs/plugin-vue@6
   ```
   > jangan lupa update jika sudah ada
   ```bash
   npm update
   ```

### Konfigurasi

1. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```
   > Buka file `.env` dan perbarui bagian `DB_DATABASE=`, `DB_USERNAME=`, dan `DB_PASSWORD=` sesuai dengan pengaturan databse lokal Anda.
2. **Generate Application Key**
   ```bash
   php artisan key:generate
   ```
3. **Jalankan Database Migrations**
   ```bash
   php artisan migrate
   ```
4. **Jalankan Assets**
   ```bash
   npm run dev
   ```
5. **Jalankan Reverb**
   ```bash
   php artisan reverb:start
   ```
   > untuk menjalakan fitur `realtime`
6. **Jalankan Laravel**
   ```bash
   php artisan serve
   ```
7. **Buka Lokalhost**
   ```bash
   http://localhost:8000
   ```

## 🤝 Contributing

We welcome contributions! Please follow these steps to contribute to the project using the **Feature Branch Workflow**:

1. **Pull the latest changes**
   Before starting, ensure your local main branch is up to date.
   ```bash
   git checkout main
   git pull origin main
   ```
2. **Create a New Branch**
   Create a branch for your feature or fix. Use a descriptive name (e.g., `feature/login-page` or `fix/nav-bar`).
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Changes & Commit**
   Write your code and commit your changes with a clear message.
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   ```
4. **Push to the Branch**
   Push your branch to the repository.
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a Pull Request (PR)**
   - Go to the repository on GitHub.
   - You will see a "Compare & pull request" button.
   - Click it, add a description of your work, and submit the PR.
   - Wait for a code review before merging.

## About Laravel

Laravel is a web application framework with expressive, elegant syntax. We believe development must be an enjoyable and creative experience to be truly fulfilling. Laravel takes the pain out of development by easing common tasks used in many web projects, such as:

- [Simple, fast routing engine](https://laravel.com/docs/routing).
- [Powerful dependency injection container](https://laravel.com/docs/container).
- Multiple back-ends for [session](https://laravel.com/docs/session) and [cache](https://laravel.com/docs/cache) storage.
- Expressive, intuitive [database ORM](https://laravel.com/docs/eloquent).
- Database agnostic [schema migrations](https://laravel.com/docs/migrations).
- [Robust background job processing](https://laravel.com/docs/queues).
- [Real-time event broadcasting](https://laravel.com/docs/broadcasting).

Laravel is accessible, powerful, and provides tools required for large, robust applications.

## Learning Laravel

Laravel has the most extensive and thorough [documentation](https://laravel.com/docs) and video tutorial library of all modern web application frameworks, making it a breeze to get started with the framework. You can also check out [Laravel Learn](https://laravel.com/learn), where you will be guided through building a modern Laravel application.

If you don't feel like reading, [Laracasts](https://laracasts.com) can help. Laracasts contains thousands of video tutorials on a range of topics including Laravel, modern PHP, unit testing, and JavaScript. Boost your skills by digging into our comprehensive video library.

## Laravel Sponsors

We would like to extend our thanks to the following sponsors for funding Laravel development. If you are interested in becoming a sponsor, please visit the [Laravel Partners program](https://partners.laravel.com).

### Premium Partners

- **[Vehikl](https://vehikl.com)**
- **[Tighten Co.](https://tighten.co)**
- **[Kirschbaum Development Group](https://kirschbaumdevelopment.com)**
- **[64 Robots](https://64robots.com)**
- **[Curotec](https://www.curotec.com/services/technologies/laravel)**
- **[DevSquad](https://devsquad.com/hire-laravel-developers)**
- **[Redberry](https://redberry.international/laravel-development)**
- **[Active Logic](https://activelogic.com)**

## Contributing

Thank you for considering contributing to the Laravel framework! The contribution guide can be found in the [Laravel documentation](https://laravel.com/docs/contributions).

## Code of Conduct

In order to ensure that the Laravel community is welcoming to all, please review and abide by the [Code of Conduct](https://laravel.com/docs/contributions#code-of-conduct).

## Security Vulnerabilities

If you discover a security vulnerability within Laravel, please send an e-mail to Taylor Otwell via [taylor@laravel.com](mailto:taylor@laravel.com). All security vulnerabilities will be promptly addressed.

## License

The Laravel framework is open-sourced software licensed under the [MIT license](https://opensource.org/licenses/MIT).
