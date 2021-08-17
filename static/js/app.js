document.addEventListener('DOMContentLoaded', () => {
  (document.querySelectorAll('.notification .delete') || []).forEach(
    $delete => {
      const $notification = $delete.parentNode;

      $delete.addEventListener('click', () => {
        $notification.parentNode.removeChild($notification);
      });
    }
  );
});
// Navbar toggle
const $burger = document.querySelector('.navbar-burger');
const $navbarTogler = document.querySelector('#navbar-toggler');
$burger.addEventListener('click', () => {
  $navbarTogler.classList.toggle('is-active');
});
