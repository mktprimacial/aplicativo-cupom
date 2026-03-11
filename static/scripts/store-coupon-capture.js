(function () {
  try {
    var url = new URL(window.location.href);
    var coupon = url.searchParams.get('coupon') || url.searchParams.get('discount_code');
    var ref = url.searchParams.get('ref');

    if (coupon) {
      localStorage.setItem('coupon_by_link_coupon', coupon);
      sessionStorage.setItem('coupon_by_link_coupon', coupon);
    }

    if (ref) {
      localStorage.setItem('coupon_by_link_ref', ref);
      sessionStorage.setItem('coupon_by_link_ref', ref);
    }
  } catch (e) {
    // no-op
  }
})();
