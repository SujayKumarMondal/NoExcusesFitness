<!-- ![Login Page](images/login_page.png)
![Dashboard](images/dashboard.png)
![New Admission](images/new_admission.png)
![View All Members](images/view_all_members.png)
![Edit Member](images/edit_member.png)
![Member Attendance](images/attendance.png)
![Member Attendance](images/edit_attendance.png)
![Generate Reports](images/reports.png)
![Notifications](images/notifications.png)
![Trainer](images/trainer.png)
![Edit & Delete Trainer](images/edit_trainer.png)
![Edit & Delete Trainer](images/trainer_attendance.png)
![Edit & Delete Trainer](images/edit_trainer_attendance.png)
![Change Password](images/change_password.png) -->

# No Excuses Fitness Dashboard

A modern, user-friendly web application for managing gym memberships, trainers, payments, attendance, and more. Built with Django, this project streamlines gym administration, making it easy to track members, handle payments, generate reports, and manage trainers—all from a clean, responsive interface.

---

## Features

- **Member Management:** Add, edit, view, and delete gym members with ease.
- **Trainer Management:** Manage trainer profiles, attendance, and payments.
- **Attendance Tracking:** Record and monitor attendance for both members and trainers.
- **Payment Management:** Track payments, due dates, and generate payment reports.
- **Reporting:** Generate and export detailed reports on admissions, payments, and attendance.
- **Notifications:** Receive alerts for important events and expiring memberships.
- **User Authentication:** Secure login system with password management.
- **Customizable Dashboard:** Personalize the admin dashboard and change wallpapers.
- **Responsive UI:** Clean, mobile-friendly interface powered by Bootstrap.

---

## Screenshots

| Login Page | Dashboard | New Admission |
|------------|-----------|---------------|
| ![Login Page](images/login_page.png) | ![Dashboard](images/dashboard.png) | ![New Admission](images/new_admission.png) |

| View Members | Edit Member | Member Attendance |
|--------------|-------------|-------------------|
| ![View All Members](images/view_all_members.png) | ![Edit Member](images/edit_member.png) | ![Member Attendance](images/attendance.png) |

| Edit Attendance | Reports | Notifications |
|-----------------|---------|--------------|
| ![Edit Attendance](images/edit_attendance.png) | ![Generate Reports](images/reports.png) | ![Notifications](images/notifications.png) |

| Trainer | Edit Trainer | Trainer Attendance | Edit Trainer Attendance | Change Password |
|---------|--------------|-------------------|------------------------|-----------------|
| ![Trainer](images/trainer.png) | ![Edit & Delete Trainer](images/edit_trainer.png) | ![Trainer Attendance](images/trainer_attendance.png) | ![Edit Trainer Attendance](images/edit_trainer_attendance.png) | ![Change Password](images/change_password.png) |

---

## Getting Started

### Prerequisites

- Python 3.6+
- pip (Python package manager)
- (Optional) Virtual environment tool (e.g., `venv` or `virtualenv`)

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/SujayKumarMondal/NoExcusesFitness
    cd NoExcusesFitness
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Apply migrations:**
    ```sh
    python manage.py migrate
    ```

4. **Create a superuser:**
    ```sh
    python manage.py createsuperuser
    # Follow the prompts to set up your admin account
    ```

5. **Run the development server:**
    ```sh
    python manage.py runserver
    ```

6. **Access the application:**
    - Open your browser and go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) or your defined port.

---

## Usage

- **Login:** Use your admin credentials to log in.
- **Dashboard:** View statistics, quick links, and notifications.
- **Members:** Add, view, and manage gym members.
- **Trainers:** Manage trainer profiles and attendance.
- **Attendance:** Mark and review attendance records.
- **Payments:** Record payments and view payment history.
- **Reports:** Generate and export reports for admissions and payments.
- **Settings:** Change your password and customize the dashboard appearance.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements and bug fixes.

---

## Acknowledgements

- Built with [Django](https://www.djangoproject.com/)
- UI powered by [Bootstrap](https://getbootstrap.com/)
- Icons from [Font Awesome](http://fontawesome.io/)

---

## Contact

For questions or support, please contact [Sujay Kumar Mondal](mailto:hiiiamsujay12@gmail.com).