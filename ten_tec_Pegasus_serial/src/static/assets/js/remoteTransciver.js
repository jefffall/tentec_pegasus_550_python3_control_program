scan_band_toggle = 0;

function process_scan_link_click(scan_freq) {
         scan_band_toggle = 0;
         $("#scan_band_1000").removeClass('btn-warning');
         $("#scan_band_100").removeClass('btn-warning');
         set_rx_freq(scan_freq);
         }
 
function set_rx_freq(freq) {

        $.getJSON("set_rx_freq", {
            freq: freq,
            format: "json"
        })
        freq_tuned_to = freq;
    };

$(document).ready(function() {

    var current_freq = "Waiting for program start";
    var current_filter = "";
    var local_rx_freq = 10001500;
    var local_tx_freq = 10001500;
    var freq_tuned_to = 72500000;
    var local_mode = "";
    //var local_volume = 0;
    var previous_mode = "";
    var peak_watts = 0;
    var s_units = 0;
    var step = 1000;
    var band = "bc";
    var set_volume_by_knob = 0;
    var reported_volume = 0;
    var speaker_volume = "0";
    var set_filter_by_knob = 0;
    var rx_freq_in_pegasus = 0;
    var was_fm_15_10 = 0;
    
    //var scan_band_toggle = 0;
    var scan_freq = 0
    var scan_increment = 0
    
    var selected_band = "AAA";
    
    var increase_freq_pressed = "False";
    var decrease_freq_pressed = "False";

    var AM = "0";
    var USB = "1";
    var LSB = "2";
    var CW = "3";
    var FM = "4";
    
    var band_lower = "";
    var band_upper = "";
    
    var smeter_average = 0;
    var smeter_running_sum = 0;
    var frequency_steps = 0;
    var smeter_average_established = 0;
    var auto_squelch_toggle = 0;
    var noise_floor_established = 0;
    
    var scan_links = "";
        
    
    function print_mode(mode){
       if (mode == "0") {
           return("AM");
       }
      if (mode == "1") {
          return("USB");
      }
      if (mode == "2") {
          return("LSB");
      }
         if (mode == "3") {
          return("CW");
      }
      if (mode == "4") {
          return("FM");
      }
    
    }
    
    // Start on 40m
    set_mode(LSB);
    set_rx_filter("1500");
   
    
    jQuery.ajaxSetup({async:false});
    just_get_freq();
    //alert("Init get freq from pegasus:"+rx_freq_in_pegasus);
    jQuery.ajaxSetup({async:true});
    //set_rx_freq("7225000");
    set_rx_freq(rx_freq_in_pegasus);
    set_speaker_volume("12");
    
   $("#remote_audio_on").click(function(){
       open_and_play_mic_input();
  });
    
     $("#remote_audio_off").click(function(){
       close_mic_media()
  });
    
    $( "#minus" )
  .mouseup(function() {
    //$( this ).append( "<span style='color:#f00;'>Mouse up.</span>" );
        decrease_freq_pressed = "False";
  })
  .mousedown(function() {
    //$( this ).append( "<span style='color:#00f;'>Mouse down.</span>" );
    decrease_freq_pressed = "True";
  });
    
 $( "#plus" )
  .mouseup(function() {
    //$( this ).append( "<span style='color:#f00;'>Mouse up.</span>" );
   increase_freq_pressed = "False"
     
  })
  .mousedown(function() {
    //$( this ).append( "<span style='color:#00f;'>Mouse down.</span>" );
      increase_freq_pressed = "True"
  });
    
    
   
    

    $("#agc_pick a ").click(function() {
        var end = this.value;
        var clicked = $(this).text();
        set_agc(clicked);
    });


    $("#volume_pick a ").click(function() {
        var end = this.value;
        //var firstDropVal = $('#volume_picker').val();
        var clicked = $(this).text();
        set_speaker_volume(clicked);
    });

    $("#squelch_pick a ").click(function() {
        var end = this.value;
        //var firstDropVal = $('#volume_picker').val();
        var clicked = $(this).text();
        set_squelch(clicked);
    });

    $("#anr_notch_pick a ").click(function() {
        var end = this.value;
        //var firstDropVal = $('#volume_picker').val();
        var clicked = $(this).text();
        set_anr_notch(clicked);
    });

    $("#rx_filter_wide a ").click(function() {
        var end = this.value;
        //var firstDropVal = $('#volume_picker').val();
        var clicked = $(this).text();
        set_rx_filter(clicked);
    });

    $("#rx_filter_mid a ").click(function() {
        var end = this.value;
        //var firstDropVal = $('#volume_picker').val();
        var clicked = $(this).text();
        set_rx_filter(clicked);
    });

    $("#rx_filter_tight a ").click(function() {
        var end = this.value;
        var clicked = $(this).text();
        set_rx_filter(clicked);
    });

    $("#transmit_enable_pick a ").click(function() {
        var end = this.value;
        var clicked = $(this).text();
        transmit_enable(clicked);
    });

    $("#transmit_power_pick a ").click(function() {
        var end = this.value;
        var clicked = $(this).text();
        transmit_power(clicked);
    });

    $("#transmit_bandwidth_pick a ").click(function() {
        var end = this.value;
        var clicked = $(this).text();
        transmit_bandwidth(clicked);
        set_tx_freq(current_freq.replace('.', ''));
    });


    $("#mic_gain_pick a ").click(function() {
        var end = this.value;
        var clicked = $(this).text();
        mic_gain(clicked);
    });

    $("#speech_processor_pick a ").click(function() {
        var end = this.value;
        var clicked = $(this).text();
        speech_processor(clicked);
    });
    
     $("#cw_sidetone_pick a ").click(function() {
        var end = this.value;
        var clicked = $(this).text();
        cw_sidetone(clicked);
    });


    $("#tx_monitor_pick a ").click(function() {
        var end = this.value;
        var clicked = $(this).text();
        tx_monitor(clicked);
    });

    $("#tune_transmitter_pick a ").click(function() {
        var end = this.value;
        var clicked = $(this).text();
        if (clicked == "TRANSMIT ON") {
            previous_mode = local_mode;
            set_mode(FM);
        } else {
            console.log(local_mode);
            set_mode(previous_mode);
        }
        tune_transmitter(clicked);
    });

    function set_agc(speed) {

        $.getJSON("set_agc", {
            speed: speed,
            format: "json"
        })
    };

    function set_speaker_volume(volume) {

        $.getJSON("set_speaker_volume", {
            volume: volume,
            format: "json"
        })
    };

    function set_squelch(sunit) {

        $.getJSON("set_squelch", {
            sunit: sunit,
            format: "json"
        })
    };

    function set_anr_notch(state) {

        $.getJSON("set_anr_notch", {
            state: state,
            format: "json"
        })
    };


    function set_step(mystep) {

        $.getJSON("set_step", {
            step: mystep,
            format: "json"
        })
        step = mystep;
        // 1000 for FM
        if (band != "bc") {
            float_freq = parseFloat(freq_tuned_to/1000000);
            decimals = 7 - mystep.length;
            freq_float_trunc = float_freq.toFixed(decimals);
            freq_tuned_to = parseInt(freq_float_trunc*1000000);
            //console.log(freq_tuned_to);
            set_rx_freq(freq_tuned_to);
            }
    };


    function set_rx_filter(rx_filter) {

        $.getJSON("set_rx_filter", {
            rx_filter: rx_filter,
            format: "json"
        })
        set_filter = rx_filter;
        //set_rx_freq(freq_tuned_to);
    };


    function set_rx_freq(freq) {

        $.getJSON("set_rx_freq", {
            freq: freq,
            format: "json"
        })
        freq_tuned_to = freq;
    };

    function set_tx_freq(freq) {

        local_tx_freq = freq;

        $.getJSON("set_tx_freq", {
            freq: freq,
            format: "json"
        })
    };

    function transmit_enable(state) {
        $.getJSON("transmit_enable", {
            state: state,
            format: "json"
        })
    };

    function transmit_power(power) {
        $.getJSON("transmit_power", {
            power: power,
            format: "json"
        })
    };

    function transmit_bandwidth(bandwidth) {
        $.getJSON("transmit_bandwidth", {
            bandwidth: bandwidth,
            format: "json"
        })
    };

    function mic_gain(percent) {
        $.getJSON("mic_gain", {
            percent: percent,
            format: "json"
        })
    };

    function speech_processor(percent) {
        $.getJSON("speech_processor", {
            percent: percent,
            format: "json"
        })
    };
    
    function cw_sidetone(percent) {
        $.getJSON("cw_sidetone", {
            percent: percent,
            format: "json"
        })
    };

    function tx_monitor(level) {
        $.getJSON("tx_monitor", {
            level: level,
            format: "json"
        })
    };

    function tune_transmitter(state) {
        $.getJSON("tune_transmitter", {
            state: state,
            format: "json"
        })
    };


    function set_mode(mode) {
        switch (mode) {
            case "0":
                //$("#mymode").html("AM");
                local_mode = AM;
                if (band == "bc") {
                set_step("10000");
                } else {
                    //set_rx_freq(freq_tuned_to);
                    set_step("1000");
                }
                break;
            case "1":
                //$("#mymode").html("USB");
                local_mode = USB;
                set_step("100");
                //set_rx_freq(freq_tuned_to);
                break;
            case "2":
                //$("#mymode").html("LSB");
                local_mode = LSB;
                set_step("100");
                //set_rx_freq(freq_tuned_to);
                break;
            case "3":
                //$("#mymode").html("CW");
                local_mode = CW;
                set_step("10");
                set_rx_freq(freq_tuned_to);
                break;
            case "4":
                //$("#mymode").html("FM");
                local_mode = FM;
                set_step("1000");
                //set_rx_freq(freq_tuned_to);
                break;
        }


        $.getJSON("set_mode", {
            mode: mode,
            format: "json"
        })
    };


    $("button").click(function() {
        switch (this.id) {
            case "bc":
                clear_all_band_buttons();
                band = "bc";
                set_step("10000");
                set_rx_filter("8000");
                set_mode(AM);
                set_rx_freq("1280000");
                set_relative_volume("0");
                break;
            case "160":
                clear_all_band_buttons();
                $("#scan_band_100").removeClass('btn-warning');
                $("#scan_band_1000").removeClass('btn-warning');
                scan_band_toggle = 0;
                band = "160";
                set_rx_filter("1500");
                set_rx_freq("1840000");
                set_mode(LSB);
                set_relative_volume("0");
                band_lower = parseInt("1840000");
                band_upper = parseInt("1999999");
                break;
            case "80":
                clear_all_band_buttons();
                $("#scan_band_100").removeClass('btn-warning');
                $("#scan_band_1000").removeClass('btn-warning');
                scan_band_toggle = 0;
                band = "80";
                set_rx_filter("1500");
                set_rx_freq("3573000");
                set_mode(LSB);
                set_relative_volume("0");
                band_lower = parseInt("3574000");
                band_upper = parseInt("3999999");
                break;
            case "60":
                clear_all_band_buttons();
                $("#scan_band_100").removeClass('btn-warning');
                $("#scan_band_1000").removeClass('btn-warning');
                scan_band_toggle = 0;
                band = "60";
                set_rx_filter("1500");
                set_rx_freq("5357000");
                set_mode(LSB);
                set_relative_volume("1");
                band_lower = parseInt("5250000");
                band_upper = parseInt("5450000");
                break;
            case "40":
                clear_all_band_buttons();
                $("#scan_band_100").removeClass('btn-warning');
                $("#scan_band_1000").removeClass('btn-warning');
                scan_band_toggle = 0;
                band = "40";
                set_rx_filter("1500");
                set_rx_freq("7074000");
                set_mode(LSB);
                set_relative_volume("2");
                band_lower = parseInt("7100000");
                band_upper = parseInt("7299999");
                break;
            case "30":
                clear_all_band_buttons();
                $("#scan_band_100").removeClass('btn-warning');
                $("#scan_band_1000").removeClass('btn-warning');
                scan_band_toggle = 0;
                band = "30";
                set_rx_filter("1500");
                set_rx_freq("10136000");
                set_mode(USB);
                set_relative_volume("2");
                band_lower = parseInt("10138000");
                band_upper = parseInt("10150000");
                break;
            case "20":
                clear_all_band_buttons();
                $("#scan_band_100").removeClass('btn-warning');
                $("#scan_band_1000").removeClass('btn-warning');
                scan_band_toggle = 0;
                band = "20";
                set_rx_filter("1500");
                set_rx_freq("14074000");
                set_mode(USB);
                set_relative_volume("3");
                band_lower = parseInt("14076000");
                band_upper = parseInt("14350000");
                break
            case "17":
                clear_all_band_buttons();
                $("#scan_band_100").removeClass('btn-warning');
                $("#scan_band_1000").removeClass('btn-warning');
                scan_band_toggle = 0;
                band = "17";
                set_rx_filter("1500");
                set_rx_freq("18100000");
                set_mode(USB);
                set_relative_volume("6");
                band_lower = parseInt("18110000");
                band_upper = parseInt("18168000");
                break;
            case "15":
                clear_all_band_buttons();
                $("#scan_band_100").removeClass('btn-warning');
                $("#scan_band_1000").removeClass('btn-warning');
                scan_band_toggle = 0;
                band = "15";
                set_rx_filter("1500");
                set_rx_freq("21074000");
                set_mode(USB);
                set_relative_volume("6");
                band_lower = parseInt("21076000");
                band_upper = parseInt("21450000");
                break;
            case "12":
                clear_all_band_buttons();
                $("#scan_band_100").removeClass('btn-warning');
                $("#scan_band_1000").removeClass('btn-warning');
                scan_band_toggle = 0;
                band = "12";
                set_rx_filter("1500");
                set_rx_freq("24915000");
                set_mode(USB);
                set_relative_volume("10");
                band_lower = parseInt("24917000");
                band_upper = parseInt("24990000");
                break;
            case "10":
                clear_all_band_buttons();
                $("#scan_band_100").removeClass('btn-warning');
                $("#scan_band_1000").removeClass('btn-warning');
                scan_band_toggle = 0;
                band = "10";
                set_rx_filter("1500");
                set_rx_freq("28074000");
                set_mode(USB);
                set_relative_volume("10");
                local_volume = "112";
                band_lower = parseInt("28074000");
                band_upper = parseInt("29700000");
                break;
            case "wwv025":
                clear_all_band_buttons();
                $("#wwv025").addClass('btn-warning');
                set_mode(AM);
                set_rx_filter("6000");
                set_rx_freq("2500000");
                //set_rx_freq("2500000");
                set_relative_volume("0");
                break;
            case "wwv050":
                clear_all_band_buttons();
                $("#wwv050").addClass('btn-warning');
                set_mode(AM);
                set_rx_filter("6000");
                set_rx_freq("5000000");
                //set_rx_freq("5000000");
                set_relative_volume("0");
                break;
            case "wwv10":
                clear_all_band_buttons();
                $("#wwv10").addClass('btn-warning');
                set_mode(AM);
                set_rx_filter("6000");
                set_rx_freq("10000000");
                //set_rx_freq("10000000");
                set_relative_volume("-1");
                break;
            case "wwv15":
                clear_all_band_buttons();
                $("#wwv15").addClass('btn-warning');
                set_mode(AM);
                set_rx_filter("6000");
                set_rx_freq("15000000");
                //set_rx_freq("15000000");
                set_relative_volume("-2");
                break;
            case "wwv20":
                clear_all_band_buttons();
                $("#wwv20").addClass('btn-warning');
                set_mode(AM);
                set_rx_filter("6000");
                set_rx_freq("20000000");
                //set_rx_freq("20000000");
                set_relative_volume("2");
                break;
            case "wwv25":
                clear_all_band_buttons();
                $("#wwv25").addClass('btn-warning');
                //set_step("1000");
                set_mode(AM);
                set_rx_filter("6000");
                set_rx_freq("25000000");
                //set_rx_freq("25000000");
                set_relative_volume("6");
                break;
            case "chu033":
                clear_all_band_buttons();
                $("#chu033").addClass('btn-warning');
                set_mode(AM);
                set_rx_filter("2250");
                set_rx_freq("3330000");
                //set_rx_freq("3330000");
                set_relative_volume("-2");
                break;
            case "chu0785":
                clear_all_band_buttons();
                $("#chu0785").addClass('btn-warning');
                set_mode(AM);
                set_rx_filter("2250");
                set_rx_freq("7850000");
                //set_rx_freq("7850000");
                set_relative_volume("2");
                break;
            case "chu14670":
                clear_all_band_buttons();
                $("#chu14670").addClass('btn-warning');
                set_mode(AM);
                set_rx_filter("2250");
                set_rx_freq("14670000");
                //set_rx_freq("14670000");
                set_relative_volume("3");
                break;
            case "am":
                set_mode(AM);
                set_step("1000");
                set_rx_filter("6000");
                set_rx_freq(freq_tuned_to);
                if (was_fm_15_10 == 1) {
                    was_fm_15_10 = 0;
                    set_relative_volume("15");
                 }
                if (band == "160" || band == "80" || band =="60" || band == "40" || band == "30") {
                   set_relative_volume("-5");
                   }
                else if ( band == "20" ) {
                    set_relative_volume("0");
                }
                 else if ( band == "17" ) {
                    set_relative_volume("3");
                }
                else if ( band == "15" || band == "12" || band == "10") {
                    set_relative_volume("2");
                }
                    
                break;
            case "lsb":
                set_mode(LSB);
                set_rx_filter("1500");
                set_step("100");
                set_rx_freq(freq_tuned_to);
                if (was_fm_15_10 == 1) {
                    was_fm_15_10 = 0;
                    set_relative_volume("50");
                 }
                break;
            case "usb":
                set_mode(USB);
                set_rx_filter("1500");
                set_step("100");
                set_rx_freq(freq_tuned_to);
                 if (was_fm_15_10 == 1) {
                    was_fm_15_10 = 0;
                    set_relative_volume("50");
                 }
                break;
            case "cw":
                set_mode(CW);
                set_step("10");
                set_rx_filter("900");
                set_rx_freq(freq_tuned_to);
                if (was_fm_15_10 == 1) {
                    was_fm_15_10 = 0;
                    set_relative_volume("50");
                }
                break;
            case "fm":
                set_mode(FM);
                set_step("1000");
                set_rx_filter("6000");
                set_rx_freq(freq_tuned_to);
                if (band == "12" || band == "10") {
                    set_relative_volume("15")
                    was_fm_15_10 = 1;
                }
                break;
            case "volset":
                if (set_volume_by_knob == 0) {
                    $("#volset").addClass('btn-warning');
                    set_volume_by_knob = 1;
                    set_vol_by_knob("1");
                     $("#watts").html(" ");
                    $("#watts").show();
                    break;
                }
                 else {
                    $("#volset").removeClass('btn-warning');
                    set_volume_by_knob = 0;
                    set_vol_by_knob("0");
                    $("#watts").hide();
                    break;
                }
                case "filterset":
                if (set_filter_by_knob == 0) {
                    $("#filterset").addClass('btn-warning');
                    set_filter_by_knob = 1;
                    my_set_filter_by_knob("1");
                     $("#watts").html(" ");
                    $("#watts").show();
                    break;
                }
                else {
                    $("#filterset").removeClass('btn-warning');
                    set_filter_by_knob = 0;
                    my_set_filter_by_knob("0");
                    //$("#watts").hide();
                     }
                    break;
                
               case "scan_band_100":
                scan_freq = parseInt(band_lower);
                if (scan_band_toggle == 0) {
                    scan_freq = parseInt(band_lower);
                    scan_increment = 100;
                    scan_band_toggle = 1;
                    smeter_average_established = 0;
                    scan_links = "";
                    noise_floor_established = 0;
                    $("#active_qso").text(" Establishing Noise Floor Baseline...");
                    $("#scan_band_100").addClass('btn-warning');
                    } 
                else {
                     $("#scan_band_100").removeClass('btn-warning');
                    scan_band_toggle = 0;
                    }
                break;
          
             case "scan_band_1000":
                scan_freq = parseInt(band_lower);
                if (scan_band_toggle == 0) {
                    scan_freq = parseInt(band_lower);
                    scan_increment = 1000;
                    scan_band_toggle = 1;
                    smeter_average_established = 0;
                    scan_links = "";
                    noise_floor_established = 0;
                    $("#active_qso").text(" Establishing Noise Floor Baseline...");
                    $("#scan_band_1000").addClass('btn-warning');
                    } 
                else {
                     $("#scan_band_1000").removeClass('btn-warning');
                    scan_band_toggle = 0;
                    }
                break;
                
             case "auto_squelch":
               
                if (auto_squelch_toggle == 0) {
                    auto_squelch_toggle = 1;
                    $("#auto_squelch").addClass('btn-warning');
                    } 
                else {
                     $("#auto_squelch").removeClass('btn-warning');
                    auto_squelch_toggle = 0;
                    set_squelch("S0");
                    }
                break;
                
            case "Ant_tuner_bypass":
                clear_all_antenna_tune_buttons();
                $("#Ant_tuner_bypass").addClass('btn-warning');
                ant_tuner("$0\r");
                break;
            case "Ant_autotune":
                 $("#Ant_tuner_bypass").removeClass('btn-warning');
                ant_tuner("$1\r");
                break;
            case "Ant_C_up":
                 ant_tuner("$3\r");
                break;
             case "Ant_C_down":
                ant_tuner("$4\r");
                break;
             case "Ant_L_up":
                ant_tuner("$5\r");
                break;
             case "Ant_L_down":
                ant_tuner("$6\r");
                break;
             case "Ant_High_Z":
                ant_tuner("$7\r");
                break;
             case "Ant_Low_Z":
                ant_tuner("$8\r");
                break;
            case "Ant_160":
                clear_all_antenna_tune_buttons();
                $("#Ant_160").addClass('btn-warning');
                ant_tuner_from_memory(68,20,0);
                break;
            case "Ant_80":
                clear_all_antenna_tune_buttons();
                $("#Ant_80").addClass('btn-warning');
                ant_tuner_from_memory(29,29,0);
                break;
            case "Ant_60":
                clear_all_antenna_tune_buttons();
                $("#Ant_60").addClass('btn-warning');
                ant_tuner_from_memory(41,4,0);
                break;
            case "Ant_40":
                clear_all_antenna_tune_buttons();
                $("#Ant_40").addClass('btn-warning');
                ant_tuner_from_memory(17,0,0);
                break;
            case "Ant_30":
                clear_all_antenna_tune_buttons();
                $("#Ant_30").addClass('btn-warning');
                ant_tuner_from_memory(10,10,1);
                break;
            case "Ant_20":
                clear_all_antenna_tune_buttons();
                $("#Ant_20").addClass('btn-warning');
                ant_tuner_from_memory(0,5,1);
                break;
            case "Ant_17":
                clear_all_antenna_tune_buttons();
                $("#Ant_17").addClass('btn-warning');
                ant_tuner_from_memory(0,0,0);
                break;
            case "Ant_15":
                clear_all_antenna_tune_buttons();
                $("#Ant_15").addClass('btn-warning');
                ant_tuner_from_memory(5,3,0);
                break;
            case "Ant_12":
                clear_all_antenna_tune_buttons();
                $("#Ant_12").addClass('btn-warning');
                ant_tuner_from_memory(0,0,0);
                break;
            case "Ant_10":
                clear_all_antenna_tune_buttons();
                $("#Ant_10").addClass('btn-warning');
                ant_tuner_from_memory(0,1,0);
                break;
        }
    });
    
    
     function ant_tuner(operation) {
           $.getJSON("ant_tuner", {
            ant_tuner: operation,
            format: "json"
        })
    }
    
    function ant_tuner_from_memory(capacitance, inductance, impedance) {
           $.getJSON("ant_tuner_from_memory", {
            capacitance : capacitance,
            inductance : inductance,
            impedance : impedance,
               
            format: "json"
        })
    }
    
    
    function set_vol_by_knob(value) {
           $.getJSON("set_volume_by_knob", {
            set_volume_by_knob: value,
            format: "json"
        })
    }
    
    function set_relative_volume(rel_vol) {
         $.getJSON("set_relative_volume", {
            rv: rel_vol,
            format: "json"
        })
       
       
        
    }
    
      function my_set_filter_by_knob(value) {
           $.getJSON("set_filter_by_knob", {
            set_filter_by_knob: value,
            format: "json"
        })
    }
        // ASCII ‘0’ (0x30) for AM mode
        // ASCII ‘1’ (0x31) for USB mode
        // ASCII ‘2’ (0x32) for LSB mode
        // ASCII ‘3’ (0x33) for CW mode
        // ASCII ‘4’ (0x34) for FM mode
    
    function get_smeter() {
        $.get("get_smeter", function(response) {
            var smeter = response.sm;
            var watts_forward = response.wf;
            var watts_reflected = response.wr;
            var radio_mode = response.mo;
                speaker_volume = response.vo;
            var squelch_value = response.sq;
            var anr_notch_value = response.an;
            var filter_hz = response.fi;
            var transmit_enable = response.te;
            var transmit_power = response.tp;
            var transmit_bandwidth = response.tb;
            var mic_gain = response.mg;
            var speech_processor = response.sp;
            var tx_monitor = response.tm;
            var tune_trasmitter = response.tt;
            var cw_sidetone_val = response.cs;
            
            
            $("#vol_set_value").text(speaker_volume);
            $("#volume_value").text(speaker_volume);
            if (squelch_value == "S0") {
                squelch_value = "OFF";
            }
            $("#squelch_value").text(squelch_value);
            $("#anr_notch_value").text(anr_notch_value);
            filter_hz = filter_hz + " Hz";
            $("#rx_filter_am_ssb_value").text(filter_hz);
            $("#rx_filter_ssb_cw_value").text(filter_hz);
            $("#rx_filter_cw_n_value").text(filter_hz);
            $("#filter_set_value").text(filter_hz);
            
            $("#transmit_enable_value").text(transmit_enable);
            $("#transmit_power_value").text(transmit_power);
            $("#transmit_bandwidth_value").text(transmit_bandwidth);
            $("#mic_gain_value").text(mic_gain);
            $("#speech_processor_value").text(speech_processor);
            $("#tx_monitor_value").text(tx_monitor);
            $("#tune_transmitter_value").text(tune_trasmitter);
            $("#cw_sidetone_value").text(cw_sidetone_val);
            
            if (radio_mode == "0") {
                clear_all_mode_buttons();
                $("#am").addClass('btn-warning');
                $("#mymode").html("AM");
                
            }
            else if (radio_mode == "1") {
                clear_all_mode_buttons();
                $("#usb").addClass('btn-warning');
                $("#mymode").html("USB");
            }
             else if (radio_mode == "2") {
                 clear_all_mode_buttons();
                  $("#lsb").addClass('btn-warning');
                  $("#mymode").html("LSB");
            }
             else if (radio_mode == "3") {
                 clear_all_mode_buttons();
                  $("#cw").addClass('btn-warning');
                  $("#mymode").html("CW");
            }
             else if (radio_mode == "4") {
                 clear_all_mode_buttons();
                  $("#fm").addClass('btn-warning');
                  $("#mymode").html("FM");
            }
            else {
                alert ("bad mode received from Pegasus: "+radio_mode);
            }
            reported_volume = response.vo;
            reported_filter = response.fi;
            if (set_volume_by_knob == 1) {
                $("#watts").html("<b>Volume: "+reported_volume+"</b>");
                }
            //else if (set_filter_by_knob == 1) {
                //$("#watts").html("<b>Filter: "+reported_filter+" Hz</b>");
                //}
            else {
            $("#watts").show()
            $("#watts").html("<b>Filter: "+reported_filter+" Hz</b>");
            if (smeter > -1) {
                //$("#watts").hide();
                peak_watts = 0;
                //$("#watts").html(peak_watts + " watts fwd "+watts_reflected+" watts reflected ");
                document.getElementById("#s_meter").value = smeter / 17.0;
                s_units = response.sm;
                $("#smeter_value").html("<b>S " + s_units + "</b>").css("background-color","white").css('color', 'black');
            } else {
                document.getElementById("#s_meter").value = 0;
                $("#smeter_value").html("<b>TRANSMITTING  "+ print_mode(local_mode)+"</b>").css("background-color","red").css('color', 'white');
                //$("#smeter_value").html('"<FONT COLOR="#ff0000"></FONT><b>TRANSMITTING</b><FONT COLOR="#000000"></FONT>"');
                if (watts_forward > peak_watts) {
                    peak_watts = watts_forward;
                }
                $("#watts").show();
                $("#watts").html("<b>WATTS - FWD: "+watts_forward+" REF: "+watts_reflected+" PEAK: "+peak_watts+"</b>");
              }
            }
        });
    }
    
    function just_get_freq() {
        $.get("get_freq", function(response) {
            rx_freq_in_pegasus = response.freq.replace(".", "");
             });
    }
            

    function get_freq() {
        $.get("get_freq", function(response) {
            
            freq_tuned_to = response.freq.replace(".", "");

            local_rx_freq = parseFloat(response.freq);
            if (local_rx_freq >= .530 && local_rx_freq <= 1.710) {
                 var freq_mhz = local_rx_freq.toFixed(slice_num);
                $("#myfreq").html(parseInt(local_rx_freq * 1000.0));
            } else {
                var slice_num = 7 - step.length;
                var freq_mhz = local_rx_freq.toFixed(slice_num);
                $("#myfreq").html(freq_mhz);
            }
            if (local_rx_freq >= .530 && local_rx_freq <= 1.710) {
                $("#bc").addClass('btn-warning');
                $("#band_info").html("AM Broadcast Band");
            } else if (freq_mhz >= 1.801 && freq_mhz <= 1.9999) {
                $("#160").addClass('btn-warning');
                $("#band_info").html("160m General, Advanced, Extra CW, AM, SSB");
            } else if (freq_mhz >= 3.5000 && freq_mhz < 4.0000) {
                $("#80").addClass('btn-warning');
                $("#band_info").html("80m ");
                if (freq_mhz >= 3.6000 && freq_mhz <= 3.700) {
                    $("#band_info").html("80m Extra Class AM SSB only");
                } else if (freq_mhz >= 3.7000 && freq_mhz <= 3.800) {
                    $("#band_info").html("80m Advanced, Extra Class CW AM SSB");
                } else if (freq_mhz >= 3.8000 && freq_mhz <= 4.00) {
                    $("#band_info").html("80m General, Advanced, Extra Class CW AM SSB");
                } else if (freq_mhz >= 3.5000 && freq_mhz <= 3.6000) {
                    $("#band_info").html("80m CW only");
                    if (freq_mhz >= 3.5000 && freq_mhz <= 3.525) {
                        $("#band_info").html("80m CW Extra Class only");
                    }
                }
            } else if (freq_mhz >= 5.250 && freq_mhz <= 5.450) {
                $("#60").addClass('btn-warning');
                $("#band_info").html("60m CW USB DIGITAL");
                if (freq_mhz == 5.3305) {
                    $("#band_info").html("60m Channel 1");
                } else if (freq_mhz == 5.3465) {
                    $("#band_info").html("60m Channel 2");
                } else if (freq_mhz == 5.3570) {
                    $("#band_info").html("60m Channel 3");
                } else if (freq_mhz == 5.3715) {
                    $("#band_info").html("60m Channel 4");
                } else if (freq_mhz == 5.4035) {
                    $("#band_info").html("60m Channel 5");
                }

            } else if (freq_mhz >= 7.000 && freq_mhz <= 7.30000) {
                $("#40").addClass('btn-warning');
                $("#band_info").html("40m ");
                if (freq_mhz >= 7.000 && freq_mhz <= 7.025) {
                    $("#band_info").html("40m Extra Class CW only");
                } else if (freq_mhz >= 7.000 && freq_mhz <= 7.1250) {
                    $("#band_info").html("40m CW only");
                } else if (freq_mhz >= 7.125 && freq_mhz <= 7.175) {
                    $("#band_info").html("40m Advanced, Extra CW AM SSB");
                } else {
                    $("#band_info").html("40m General, Advanced, Extra CW AM SSB");
                }
            } else if (freq_mhz >= 10.1 && freq_mhz <= 10.150) {
                $("#30").addClass('btn-warning');
                $("#band_info").html("30m CW & FT8 only");

            } else if (freq_mhz >= 14.000 && freq_mhz <= 14.35000) {
                $("#20").addClass('btn-warning');
                $("#band_info").html("20m ");
                if (freq_mhz >= 14.000 && freq_mhz <= 14.025) {
                    $("#band_info").html("20m Extra Class CW only");
                } else if (freq_mhz >= 14.000 && freq_mhz <= 14.1500) {
                    $("#band_info").html("20m CW only");
                } else if (freq_mhz >= 14.150 && freq_mhz <= 14.175) {
                    $("#band_info").html("20m Extra CW AM SSB");
                } else if (freq_mhz >= 14.175 && freq_mhz <= 14.225) {
                    $("#band_info").html("20m Advanced, Extra CW AM SSB");
                } else {
                    $("#band_info").html("20m General, Advanced, Extra CW AM SSB");
                }
            } else if (freq_mhz >= 18.068 && freq_mhz <= 18.168) {
                $("#17").addClass('btn-warning');
                $("#band_info").html("17m General, Advanced Extra CW AM SSB");
                if (freq_mhz >= 18.068 && freq_mhz <= 18.1100) {
                    $("#band_info").html("17m CW only");
                }
            } else if (freq_mhz >= 21.000 && freq_mhz <= 21.45000) {
                $("#15").addClass('btn-warning');
                $("#band_info").html("15m ");
                if (freq_mhz >= 21.000 && freq_mhz <= 21.025) {
                    $("#band_info").html("15m Extra Class CW only");
                } else if (freq_mhz >= 21.000 && freq_mhz <= 21.2000) {
                    $("#band_info").html("15m CW only");
                } else if (freq_mhz >= 21.200 && freq_mhz <= 21.225) {
                    $("#band_info").html("15m Extra CW AM SSB");
                } else if (freq_mhz >= 21.225 && freq_mhz <= 21.275) {
                    $("#band_info").html("15m Advanced, Extra CW AM SSB");
                } else {
                    $("#band_info").html("15m General, Advanced, Extra CW AM SSB");
                }
            } else if (freq_mhz >= 24.890 && freq_mhz <= 24.990) {
                $("#12").addClass('btn-warning');
                $("#band_info").html("12m General, Advanced, Extra CW AM SSB");
                if (freq_mhz >= 24.890 && freq_mhz <= 24.930) {
                    $("#band_info").html("12m CW only");
                }
            } else if (freq_mhz >= 28.000 && freq_mhz <= 29.700) {
                $("#10").addClass('btn-warning');
                $("#band_info").html("10m  ");
                if (freq_mhz >= 28.000 && freq_mhz <= 28.3000) {
                    $("#band_info").html("10m General, Advanced Extra CW only");
                } else if (freq_mhz >= 28.300 && freq_mhz <= 28.5000) {
                    $("#band_info").html("10m Novice, General, Advanced, Extra CW only");
                } else if (freq_mhz >= 29.520 && freq_mhz <= 29.700) {
                    $("#band_info").html("10m General, Advanced, Extra FM CW AM SSB");
                } else {
                    $("#band_info").html("10m General, Advanced, Extra CW AM SSB");
                }
            
        
            } else if (freq_mhz == 2.5 ||  freq_mhz == 10.0  ||
              freq_mhz == 15.00 ) {
                if (freq_mhz == 2.5) {
                    $("#wwv025").addClass('btn-warning');
                }
                else if (freq_mhz == 10.0) {
                     $("#wwv10").addClass('btn-warning');
                }
                else {
                     $("#wwv15").addClass('btn-warning');
                }
                 $("#band_info").html("WWV & WWVH");
            } else if (freq_mhz == 5.0 || freq_mhz == 20.0 || freq_mhz == 25.0) {
                if (freq_mhz == 5.0) {
                    $("#wwv050").addClass('btn-warning');
                }
                else if (freq_mhz == 20.0) {
                     $("#wwv20").addClass('btn-warning');
                }
                else {
                     $("#wwv25").addClass('btn-warning');
                }
                 $("#band_info").html("WWV & WWVH");
                 $("#band_info").html("WWV");
             } else if (freq_mhz == 3.33 || freq_mhz == 7.85 ||
              freq_mhz == 14.670 ) {
                  if (freq_mhz == 3.33) {
                    $("#chu033").addClass('btn-warning');
                }
                else if (freq_mhz == 7.85) {
                     $("#chu0785").addClass('btn-warning');
                }
                else {
                     $("#chu14670").addClass('btn-warning');
                }
                 $("#band_info").html("CHU Canada");
            //  It is authorized 40 channels between 26.965 MHz and 27.405 MHz.
             } else if (freq_mhz >= 26.965 && freq_mhz <= 27.405) {
                $("#band_info").html("CB Band");

                if (freq_mhz == 26.9650) {
                    $("#band_info").html("CB Channel: 1");
                } else if (freq_mhz == 26.9750) {
                    $("#band_info").html("CB Channel: 2");
                } else if (freq_mhz == 26.9850) {
                    $("#band_info").html("CB Channel: 3");
                } else if (freq_mhz == 27.0050) {
                    $("#band_info").html("CB Channel: 4");
                } else if (freq_mhz == 27.0150) {
                    $("#band_info").html("CB Channel: 5");
                } else if (freq_mhz == 27.0250) {
                    $("#band_info").html("CB Channel: 6");
                } else if (freq_mhz == 27.0350) {
                    $("#band_info").html("CB Channel: 7");
                } else if (freq_mhz == 27.0550) {
                    $("#band_info").html("CB Channel: 8");
                } else if (freq_mhz == 27.0650) {
                    $("#band_info").html("CB Channel: 9");
                } else if (freq_mhz == 27.0750) {
                    $("#band_info").html("CB Channel: 10");
                } else if (freq_mhz == 27.0850) {
                    $("#band_info").html("CB Channel: 11");
                } else if (freq_mhz == 27.1050) {
                    $("#band_info").html("CB Channel: 12");
                } else if (freq_mhz == 27.1150) {
                    $("#band_info").html("CB Channel: 13");
                } else if (freq_mhz == 27.1250) {
                    $("#band_info").html("CB Channel: 14");
                } else if (freq_mhz == 27.1350) {
                    $("#band_info").html("CB Channel: 15");
                } else if (freq_mhz == 27.1550) {
                    $("#band_info").html("CB Channel: 16");
                } else if (freq_mhz == 27.1650) {
                    $("#band_info").html("CB Channel: 17");
                } else if (freq_mhz == 27.1750) {
                    $("#band_info").html("CB Channel: 18");
                } else if (freq_mhz == 27.1850) {
                    $("#band_info").html("CB Channel: 19");
                } else if (freq_mhz == 27.2050) {
                    $("#band_info").html("CB Channel: 20");
                } else if (freq_mhz == 27.2150) {
                    $("#band_info").html("CB Channel: 21");
                } else if (freq_mhz == 27.2250) {
                    $("#band_info").html("CB Channel: 22");
                } else if (freq_mhz == 27.2550) {
                    $("#band_info").html("CB Channel: 23");
                } else if (freq_mhz == 27.2350) {
                    $("#band_info").html("CB Channel: 24");
                } else if (freq_mhz == 27.2450) {
                    $("#band_info").html("CB Channel: 25");
                } else if (freq_mhz == 27.2650) {
                    $("#band_info").html("CB Channel: 26");
                } else if (freq_mhz == 27.2750) {
                    $("#band_info").html("CB Channel: 27");
                } else if (freq_mhz == 27.2850) {
                    $("#band_info").html("CB Channel: 28");
                } else if (freq_mhz == 27.2950) {
                    $("#band_info").html("CB Channel: 29");
                } else if (freq_mhz == 27.3050) {
                    $("#band_info").html("CB Channel: 30");
                } else if (freq_mhz == 27.3150) {
                    $("#band_info").html("CB Channel: 31");
                } else if (freq_mhz == 27.3250) {
                    $("#band_info").html("CB Channel: 32");
                } else if (freq_mhz == 27.3350) {
                    $("#band_info").html("CB Channel: 33");
                } else if (freq_mhz == 27.3450) {
                    $("#band_info").html("CB Channel: 34");
                } else if (freq_mhz == 27.3550) {
                    $("#band_info").html("CB Channel: 35");
                } else if (freq_mhz == 27.3650) {
                    $("#band_info").html("CB Channel: 36");
                } else if (freq_mhz == 27.3750) {
                    $("#band_info").html("CB Channel: 37");
                } else if (freq_mhz == 27.3850) {
                    $("#band_info").html("CB Channel: 38");
                } else if (freq_mhz == 27.3950) {
                    $("#band_info").html("CB Channel: 39");
                } else if (freq_mhz == 27.4050) {
                    $("#band_info").html("CB Channel: 40");
                }
            } else if (selected_band !== band) {
                clear_all_band_buttons();
                selected_band = band;
                   }
              else {
                     $("#band_info").html(" ");
                     clear_all_band_buttons();
                   }
            return response.freq.replace(".", "");
        });
    }
    
    function clear_all_mode_buttons() {
        $("#am").removeClass('btn-warning');
        $("#lsb").removeClass('btn-warning');
        $("#usb").removeClass('btn-warning');
        $("#cw").removeClass('btn-warning');
        $("#fm").removeClass('btn-warning');
    }
    
    
    function clear_all_band_buttons() {
        $("#bc").removeClass('btn-warning');
        $("#160").removeClass('btn-warning');
        $("#80").removeClass('btn-warning');
        $("#60").removeClass('btn-warning');
        $("#40").removeClass('btn-warning');
        $("#30").removeClass('btn-warning');
        $("#20").removeClass('btn-warning');
        $("#17").removeClass('btn-warning');
        $("#15").removeClass('btn-warning');
        $("#12").removeClass('btn-warning');
        $("#10").removeClass('btn-warning');
        $("#wwv025").removeClass('btn-warning');
        $("#wwv050").removeClass('btn-warning');
        $("#wwv10").removeClass('btn-warning');
        $("#wwv15").removeClass('btn-warning');
        $("#wwv20").removeClass('btn-warning');
        $("#wwv25").removeClass('btn-warning');
        $("#chu033").removeClass('btn-warning');
        $("#chu0785").removeClass('btn-warning');
        $("#chu14670").removeClass('btn-warning');
    }
    
    function clear_all_antenna_tune_buttons() {
        $("#Ant_160").removeClass('btn-warning');
        $("#Ant_80").removeClass('btn-warning');
        $("#Ant_60").removeClass('btn-warning');
        $("#Ant_40").removeClass('btn-warning');
        $("#Ant_30").removeClass('btn-warning');
        $("#Ant_20").removeClass('btn-warning');
        $("#Ant_17").removeClass('btn-warning');
        $("#Ant_15").removeClass('btn-warning');
        $("#Ant_12").removeClass('btn-warning');
        $("#Ant_10").removeClass('btn-warning');
        $("#Ant_tuner_bypass").removeClass('btn-warning');
        
    }
    // stop only mic
function stopAudioOnly(stream) {
    stream.getTracks().forEach(function(track) {
        if (track.readyState == 'live' && track.kind === 'audio') {
            track.stop();
        }
    });
}
    
 
    function open_and_play_mic_input()
    {
        
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;

    var aCtx;
    var analyser;
    var microphone;
    if (navigator.getUserMedia) {
        navigator.getUserMedia({
        audio: true
         },
    function(stream) {
      aCtx = new AudioContext();
      microphone = aCtx.createMediaStreamSource(stream);
      var destination = aCtx.destination;
      microphone.connect(destination);
    },
    function() {
      console.log("Error 003.")
    }
  );
}

        
        
        
        
    }


    function readFiles(event) {
        var fileList = event.target.files;
        for (var i = 0; i < fileList.length; i++) {
            loadAsText(fileList[i]);
        }
    }

    function loadAsText(theFile) {
        var reader = new FileReader();

        reader.onload = function(loadedEvent) {
            // result contains loaded file.
            const file = event.target.result;
            const allLines = file.split(/\r\n|\n/);
            process_delete_storage_list(allLines);
        }
        reader.readAsText(theFile);
    }


    function process_delete_storage_list(file_lines) {
        var arrayLength = file_lines.length;
        //alert("Warning! You are about to delete "+arrayLength+" QTrees or Volumes. Are you SURE? IF not, CLOSE this browser now...")
        for (var i = 0; i < arrayLength; i++) {
            console.log(file_lines[i]);
            $("#queued_notification").val = file_lines[i]
            delete_storage(file_lines[i]);
            //Call AJAX here to put each line in the queue.
        }
        $("#myform")[0].reset();
        $("#fileinput").addClass('d-none');
        $("#uploadcsv").removeClass('d-none');
        $("#commit_delete_button").removeClass('d-none');
        $("#storage_to_delete").removeClass('d-none');
    }

    function increment_tuning_freq()
    {
    if (increase_freq_pressed == "True") {
        var int_local_rx_freq = parseFloat(local_rx_freq);
        int_local_rx_freq = (int_local_rx_freq * 1000000) + parseInt(step);
        set_rx_freq(int_local_rx_freq );
        }  
    }
    
    function decrement_tuning_freq()
    {
    if (decrease_freq_pressed  == "True") {
        var int_local_rx_freq = parseFloat(local_rx_freq);
        int_local_rx_freq = (int_local_rx_freq * 1000000) - parseInt(step);
        set_rx_freq(int_local_rx_freq );
        } 
    }
    
    function scan_band() {
        if (scan_band_toggle == 1) {
            scan_freq = scan_freq + scan_increment;    
            set_rx_freq(scan_freq);
            
            $.get("get_smeter", function(response) {
            var smeter = response.sm;
            var radio_mode = response.mo;
                speaker_volume = response.vo;
            var squelch_value = response.sq;
            var anr_notch_value = response.an;
            var filter_hz = response.fi;
            var transmit_enable = response.te;
            var transmit_power = response.tp;
            var transmit_bandwidth = response.tb;
            var mic_gain = response.mg;
            var speech_processor = response.sp;
            var tx_monitor = response.tm;
            var tune_trasmitter = response.tt;
            var cw_sidetone_val = response.cs;
            
                
            $("#vol_set_value").text(speaker_volume);
            $("#volume_value").text(speaker_volume);
            if (squelch_value == "S0") {
                squelch_value = "OFF";
            }
            $("#squelch_value").text(squelch_value);
            $("#anr_notch_value").text(anr_notch_value);
            filter_hz = filter_hz + " Hz";
            $("#rx_filter_am_ssb_value").text(filter_hz);
            $("#rx_filter_ssb_cw_value").text(filter_hz);
            $("#rx_filter_cw_n_value").text(filter_hz);
            $("#filter_set_value").text(filter_hz);
            
            $("#transmit_enable_value").text(transmit_enable);
            $("#transmit_power_value").text(transmit_power);
            $("#transmit_bandwidth_value").text(transmit_bandwidth);
            $("#mic_gain_value").text(mic_gain);
            $("#speech_processor_value").text(speech_processor);
            $("#tx_monitor_value").text(tx_monitor);
            $("#tune_transmitter_value").text(tune_trasmitter);
            $("#cw_sidetone_value").text(cw_sidetone_val);
                
                
                
                
                
                
                
            document.getElementById("#s_meter").value = smeter / 17.0;
            s_units = response.sm;
            $("#smeter_value").html("<b>S " + s_units + "</b>").css("background-color","white").css('color', 'black');
            })
            
            var s_units_int = parseInt(s_units);
            frequency_steps = frequency_steps + 1;
            smeter_running_sum = smeter_running_sum + parseInt(s_units_int);
            
            if (smeter_average_established == 1){ 
                if (noise_floor_established == 0) {
                    noise_floor_established = 1;
                    $("#active_qso").html("Noise floor established at  "+smeter_average.toFixed(2)+" S-units");
                }
                if (band == "160" || band == "80" || band == "60" || band == "40") {
                    if (s_units_int > smeter_average + 3) {
                      var link_title = get_date_time()+" "+scan_freq;
                      var my_link = '<a href="javascript:process_scan_link_click('+scan_freq+');">'+link_title+'</a>';
                      scan_links = scan_links + my_link + "<br>";
                      $("#active_qso").html(scan_links);
                     }
                } 
                 else {
                     if (s_units_int > smeter_average + 4) {
                      console.log(get_date_time()+" "+scan_freq);
                      var link_title = get_date_time()+" "+scan_freq;
                      var my_link = '<a href="javascript:process_scan_link_click('+scan_freq+');">'+link_title+'</a>';
                      scan_links = scan_links + my_link + "<br>";
                      $("#active_qso").html(scan_links);
                     }
                 }
            }
            
            if (scan_freq >= band_upper) {
                scan_freq = band_lower;
                smeter_average = smeter_running_sum / frequency_steps;
                smeter_average_established = 1;
                
                smeter_running_sum = 0;
                frequency_steps = 0;
                
                if (auto_squelch_toggle == 1) {
                    if (band == "160" || band == "80" || band == "60" || band == "40") {
                    squelch_level = s_units_int + 5;
                    }
                    else { 
                        squelch_level = s_units_int + 3
                    }
                    squelch_value = "S" + squelch_level.toString()
                    set_squelch(squelch_value);
                }
                 }
             }
    }

     function process_scan_link_click(scan_freq) {
         scan_band_toggle = 0;
         $("#scan_band_1000").removeClass('btn-warning');
         $("#scan_band_100").removeClass('btn-warning');
         set_rx_freq(scan_freq);
         }
    
      setInterval(function() {
        scan_band();
    }, 200);


   setInterval(function() {
        get_freq();
    }, 200);


    setInterval(function() {
        if (scan_band_toggle == 0) {
             get_smeter();
        }
    }, 400);
    
    setInterval(function() {
       increment_tuning_freq();
    }, 200);
    
    setInterval(function() {
       decrement_tuning_freq();
    }, 200);



    $("#uploadcsv").click(function() {
        $("#fileinput").removeClass('d-none');
        $("#uploadcsv").addClass('d-none');
        $("#commit_delete_button").addClass('d-none');
        $("#storage_to_delete").addClass('d-none');
    });

    startTime();

    function startTime() {
        var today = new Date();
        var h = today.getHours();
        var m = today.getMinutes();
        var s = today.getSeconds();
        m = checkTime(m);
        s = checkTime(s);
        $("#clockheading").html(h + ":" + m + ":" + s);

        var t = setTimeout(startTime, 500);
    }

    function checkTime(i) {
        if (i < 10) {
            i = "0" + i
        }; // add zero in front of numbers < 10
        return i;
    }

    // For todays date;
Date.prototype.today = function () { 
    return ((this.getDate() < 10)?"0":"") + this.getDate() +"/"+(((this.getMonth()+1) < 10)?"0":"") + (this.getMonth()+1) +"/"+ this.getFullYear();
}

// For the time now
Date.prototype.timeNow = function () {
     return ((this.getHours() < 10)?"0":"") + this.getHours() +":"+ ((this.getMinutes() < 10)?"0":"") + this.getMinutes() +":"+ ((this.getSeconds() < 10)?"0":"") + this.getSeconds();
}
    
    
function get_date_time() {
    var newDate = new Date();
    var datetime =  newDate.timeNow() + " " + newDate.today();
    return (datetime)
}
    
    


});