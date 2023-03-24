$(document).ready(function() {
    // Hide the multi-event and student-related fields by default
    $('.multi-event').hide();
    $('.single-event.event-name').hide();
    $('.single-event.student').hide();
    $('.single-event label[for="university"]').hide();
    $('.single-event select[name="university"]').hide();

    // When the event type changes, show the corresponding form
    $('#event-type').change(function() {
        if ($(this).val() === 'multi-event') {
            // $('.single-event.event-name').hide();
            // $('.single-event.student').hide();
            // $('.single-event label[for="university"]').hide();
            // $('.single-event select[name="university"]').hide();
            $('.single-event').hide();
            $('.multi-event').show();
            // $('.single-event').hide();
            // $('.single-event.student').hide();
            // $('.single-event label[for="university"]').hide();
            // $('.single-event select[name="university"]').hide();
        }
        else {
            $('.multi-event').hide();
            $('.single-event').show();
            // if ($('#student').is(':checked')) {
            //     $('.single-event.student').show();
            //     $('.single-event label[for="university"]').show();
            //     $('.single-event select[name="university"]').show();
            // } else {
            //     $('.single-event.student').hide();
            //     $('.single-event label[for="university"]').hide();
            //     $('.single-event select[name="university"]').hide();
            // }
        }
    });

    // When the form is changed, calculate the total price
    $('#booking-form').on('input', function() {
        var total = 0;

        if ($('#event-type').val() === 'multi-event') {
            // Calculate the price for multi-event
            var adultTickets = parseInt($('#adult-tickets').val() || 0);
            var childrenTickets = parseInt($('#children-tickets').val() || 0);
            var specialAdultTickets = parseInt($('#special-adult-tickets').val() || 0);
            var specialChildrenTickets = parseInt($('#special-children-tickets').val() || 0);

            total += adultTickets * 50;
            total += childrenTickets * 25;
            total += specialAdultTickets * 75;
            total += specialChildrenTickets * 50;

        } else {
            // Calculate the price for single-event
            var eventName = $('#event-name').val();
            var eventTime = $('#event-time').val();
            var isStudent = $('#student').is(':checked');

            total += 50;

            if (eventName === 'event2') {
                total += 25;
            }

            // if (eventTime === '1pm' || eventTime === '3pm') {
            //     total += 10;
            // }

            if (isStudent) {
                total -= 10;
                $('.single-event label[for="university"]').show();
                $('.single-event select[name="university"]').show();
                // var university = $('#university').val();
                //
                // if (university === 'uni2') {
                //     total -= 5;
                // }
            } else {
                $('.single-event label[for="university"]').hide();
                $('.single-event select[name="university"]').hide();
            }
        }

        // Update the total price field
        $('#total-price').val('$' + total);
    });

    // When the student checkbox is clicked, show or hide the university select field
    $('#student').click(function() {
        if ($(this).is(':checked')) {
            $('.single-event.student').show();
            $('.single-event label[for="university"]').show();
            $('.single-event select[name="university"]').show();
        } else {
            $('.single-event.student').hide();
            $('.single-event label[for="university"]').hide();
            $('.single-event select[name="university"]').hide();
        }

        // Trigger the input event to calculate the total price on page load
        $('#booking-form').trigger('input');
    });

    flatpickr("#booking-date", {
        enable: [
            {
                from: "today",
                to: new Date().fp_incr(30) // 7 days from now
            }
        ],
        altInput: true,
        altFormat: "F j, Y, l",
        dateFormat: "Y-m-d"
    });
});

