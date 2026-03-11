(function () {
  try {
    var coupon = sessionStorage.getItem('coupon_by_link_coupon') || localStorage.getItem('coupon_by_link_coupon');
    var ref = sessionStorage.getItem('coupon_by_link_ref') || localStorage.getItem('coupon_by_link_ref');

    if (!coupon && !ref) return;

    window.dispatchEvent(
      new CustomEvent('coupon_by_link_context', {
        detail: {
          coupon: coupon,
          ref: ref,
          capturedAt: new Date().toISOString(),
        },
      })
    );
  } catch (e) {
    // no-op
  }
})();
