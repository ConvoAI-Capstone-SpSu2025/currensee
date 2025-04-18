(function() {
  'use strict';

  let config;
  let settingsDialog;


   // Placeholder for API config
   function getConfig() {
    return {
      emailAddress: "johnsmith@example.com" // Change as needed for testing
    };
  }

  // Initialize the task pane
  Office.initialize = function(reason) {
    jQuery(document).ready(function() {
      config = getConfig();

 
      // Check if email is already configured
      if (config && config.emailAddress) {
        $('#configured-section').show();
        $('#email-display').text(`Configured for: ${config.emailAddress}`);
      } else {
        $('#not-configured').show();
      }

      // Generate Summary Button
      $('#generate-summary-button').on('click', function() {
        const email = $('#email-select').val().trim();

        if (!email) {
          showError('Please select a valid email address.');
          return;
        }

        // Show loading indicator
        $('#loading-indicator').show();

        // Generate the summary
        generateSummary(email, function(summary, error) {
          $('#loading-indicator').hide();
      
          if (summary) {
            // Populate the summary blocks with data
            $('#bio-summary-text').text(summary.bio);
            $('#interaction-summary-text').text(summary.interaction);
            $('#market-summary-text').text(summary.market);

            // Show the summary blocks
            $('#summary-output').show();
          } else {
            showError('Could not generate summary: ' + error);
          }
        });
      });

      // Handle copy button click
      $(document).on('click', '.copy-button', function() {
        const targetSelector = $(this).data('target');
        const text = $(targetSelector).text();
        navigator.clipboard.writeText(text).then(() => {
          alert('Copied to clipboard!');
        });
      });

      // Handle close (×) button click
      $(document).on('click', '.close-button', function() {
        const targetSelector = $(this).data('target');
        $(targetSelector).hide();
      });

      // Like button
      $(document).on('click', '.like-button', function() {
        $(this).text('✅ Liked').prop('disabled', true);
      });

      // Unlike button removes the block
      $(document).on('click', '.unlike-button', function() {
        const targetSelector = $(this).data('target');
        $(targetSelector).slideUp(300, function () {
          $(this).remove();
        });
      });


        // Generate the summary (if in portion of an email body)
        //generateSummary(email, function(summaryText, error) {
        //  if (summaryText) {
        //    Office.context.mailbox.item.body.setSelectedDataAsync(summaryText, { coercionType: Office.CoercionType.Text },
        //      function(result) {
        //        if (result.status === Office.AsyncResultStatus.Failed) {
        //          showError('Could not generate summary: ' + result.error.message);
        //        }
        //      });
        //  } else {
        //    showError('Could not generate summary: ' + error);
        //  }
        //});
      //});


      // Settings icon to configure email addresses
      $('#settings-icon').on('click', function() {
        const url = new URI('../src/settings/dialog.html').absoluteTo(window.location).toString();
        const dialogOptions = { width: 30, height: 40, displayInIframe: true };

        Office.context.ui.displayDialogAsync(url, dialogOptions, function(result) {
          settingsDialog = result.value;
          settingsDialog.addEventHandler(Microsoft.Office.WebExtension.EventType.DialogMessageReceived, receiveMessage);
          settingsDialog.addEventHandler(Microsoft.Office.WebExtension.EventType.DialogEventReceived, dialogClosed);
        });
      });

      // Populate the email dropdown dynamically from backend
      populateEmailDropdown();
    });
  };

  // Populate email dropdown with data from the backend
  //function populateEmailDropdown() {
  //  $.ajax({
  //    url: '/api/emails',  // Replace with backend URL
  //    method: 'GET',
  //    success: function(response) {
  //      if (response && response.emails) {
  //        const emailDropdown = $('#email-select');
  //       response.emails.forEach(function(email) {
  //          emailDropdown.append(new Option(email, email));
  //        });
  //      }
  //    },
  //    error: function(error) {
  //      showError('Failed to load email addresses from the server.');
  //    }
  //  });
  //}

//mock function to populate email dropdown
  function populateEmailDropdown() {
    const emailDropdown = $('#email-select');
  
    // Mock email addresses for testing
    const mockEmails = [
      "johnsmith@example.com",
      "janedoe@example.com",
      "demo@example.com"
    ];
  
    mockEmails.forEach(function(email) {
      emailDropdown.append(new Option(email, email));
    });
  }

  // Open Task Pane function (triggered by ribbon button click)
  function openTaskPane(event) {
    Office.context.ui.displayDialogAsync('https://localhost:3000/taskpane.html',
      { width: 30, height: 40 }, function(result) {
        settingsDialog = result.value;
        settingsDialog.addEventHandler(Microsoft.Office.WebExtension.EventType.DialogMessageReceived, receiveMessage);
        settingsDialog.addEventHandler(Microsoft.Office.WebExtension.EventType.DialogEventReceived, dialogClosed);
      });
  }

  // Handle dialog message received
  function receiveMessage(message) {
    config = JSON.parse(message.message);
    setConfig(config, function(result) {
      settingsDialog.close();
      settingsDialog = null;
      $('#not-configured').hide();
      $('#configured-section').show();
      $('#email-display').text(`Configured for: ${config.emailAddress}`);
    });
  }

  // Handle dialog closed
  function dialogClosed(message) {
    settingsDialog = null;
  }

  // Mock summary for testing
  function generateSummary(email, callback) {
    setTimeout(function() {
      const mockSummaries = {
        "johnsmith@example.com": {
          bio: "John Smith is a senior product manager at Acme Corp with a background in finance.",
          interaction: "Asked about pricing updates and scheduled a follow-up demo last week.",
          market: "Acme's stock rose 3% this quarter with notable product growth in cloud services."
        },
        "janedoe@example.com": {
          bio: "Jane Doe is the head of procurement at InnovateX with experience in B2B vendor relationships.",
          interaction: "Confirmed the contract, requested onboarding details, and mentioned Q2 budget expansion.",
          market: "InnovateX saw stable performance with a 1.5% revenue increase YOY."
        }
      };
  
      const summary = mockSummaries[email.toLowerCase()] || {
        bio: `No bio available for ${email}.`,
        interaction: `No interaction history available for ${email}.`,
        market: `No market data available for ${email}.`
      };
  
      callback(summary, null);
    }, 1000);
  }

})();