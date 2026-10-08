import customtkinter as ctk
from tkcalendar import DateEntry # For a nicer date picker
import datetime

# --- Configuration (from original script) ---
TIERS_CONFIG = [
    {"id": 1, "rate": 4.35, "cumulative_max_kwh": 50},
    {"id": 2, "rate": 4.85, "cumulative_max_kwh": 75},
    {"id": 3, "rate": 6.63, "cumulative_max_kwh": 200},
    {"id": 4, "rate": 6.95, "cumulative_max_kwh": 300},
    {"id": 5, "rate": 7.34, "cumulative_max_kwh": 400},
    {"id": 6, "rate": 7.34, "cumulative_max_kwh": float('inf')}
]

# --- UPDATED Backend Calculation Logic ---
def calculate_tiered_cost_for_x(kwh_this_segment, kwh_already_consumed_this_month):
    """
    Calculates X's electricity cost based on SLAB rates.
    The rate is determined by X's total consumption in the month.
    The returned cost is for the TOTAL KWH consumed by X in the month up to the end of the segment,
    calculated at the determined slab rate.
    """
    # This function now returns:
    # 1. cost_for_total_monthly_kwh (float): The total value of X's consumption for the month at the determined rate.
    # 2. actual_rate_used (float): The slab rate that was applied.
    # 3. total_monthly_kwh_for_x (float): The total KWH used for rate determination.
    # 4. error_message (str): Empty if no error, otherwise an error message.

    if kwh_this_segment < 0: # Should ideally be caught before calling
        # For GUI, we'll return an error indicator
        return 0.0, 0.0, 0.0, "Error: Negative KWH in segment."
    
    if kwh_already_consumed_this_month < 0:
        # For GUI, treat as 0 but could also be an error/warning
        kwh_already_consumed_this_month = 0

    total_monthly_kwh_for_x = round(kwh_this_segment + kwh_already_consumed_this_month, 2)
    
    if total_monthly_kwh_for_x <= 0: # If total effective consumption is zero or less.
        return 0.0, 0.0, 0.0, "" # No cost, no rate applicable if no consumption
        
    chosen_rate = 0.0
    found_rate = False
    for tier in TIERS_CONFIG:
        if total_monthly_kwh_for_x <= tier["cumulative_max_kwh"]:
            chosen_rate = tier["rate"]
            found_rate = True
            break
    
    if not found_rate: # Should not happen with float('inf') in last tier
        # This case indicates a logic flaw or unexpected KWH value if TIERS_CONFIG is correct
        # For GUI, return an error or use a default
        return 0.0, 0.0, total_monthly_kwh_for_x, "Error: Could not determine rate."


    # Calculate the total value of X's consumption for the month at this rate
    total_value_for_month = total_monthly_kwh_for_x * chosen_rate
    return round(total_value_for_month, 2), chosen_rate, total_monthly_kwh_for_x, ""


class ACBillSplitterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AC Bill Splitter Deluxe ⚡️")
        self.geometry("680x750") 
        ctk.set_appearance_mode("Dark") 
        
        self.APP_BG_COLOR = "#1A202C"      
        self.CARD_COLOR = "#2D3748"        
        self.ACCENT_COLOR = "#DD6B20"      
        self.ACCENT_HOVER_COLOR = "#C05621" 
        self.TEXT_COLOR = "#F7FAFC"        
        self.SECONDARY_TEXT_COLOR = "#A0AEC0"
        self.ERROR_COLOR = "#E53E3E"       
        self.BORDER_COLOR = "#4A5568"      
        self.DATE_ENTRY_FIELD_BG = "#3B475C" 
        self.SUCCESS_COLOR = "#38A169" # Green for success/positive values

        self.configure(fg_color=self.APP_BG_COLOR)

        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent") 
        self.main_container.pack(pady=15, padx=15, fill="both", expand=True)
        
        self.app_font = ("Segoe UI", 13)
        self.header_font = ("Segoe UI", 17, "bold") 
        self.small_font = ("Segoe UI", 11)
        self.result_font = ("Segoe UI", 15, "bold") 

        self.create_billing_cycle_card()
        self.create_meter_readings_card() 
        self.create_monthly_details_cards_container()
        self.create_calculate_button()
        self.create_results_card()
        self.create_y_context_card()

        self.calculate_button.configure(state="disabled")
        self.results_card.pack_forget()
        self.y_context_card.pack_forget()

    def create_styled_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=self.CARD_COLOR, corner_radius=10) 
        card.pack(pady=12, padx=5, fill="x") 
        return card

    def create_billing_cycle_card(self):
        self.billing_cycle_card = self.create_styled_card(self.main_container)
        
        ctk.CTkLabel(self.billing_cycle_card, text="📅 Billing Cycle Info", font=self.header_font, text_color=self.TEXT_COLOR).pack(pady=(15,10), padx=20, anchor="w")

        ctk.CTkLabel(self.billing_cycle_card, text="Start Date:", font=self.app_font, text_color=self.SECONDARY_TEXT_COLOR).pack(anchor="w", padx=20, pady=(5,0))
        
        self.start_date_entry = DateEntry(self.billing_cycle_card, width=18, 
                                          date_pattern='yyyy-mm-dd',
                                          font=self.app_font,
                                          background=self.ACCENT_COLOR, 
                                          foreground=self.TEXT_COLOR,   
                                          bordercolor=self.BORDER_COLOR,
                                          selectbackground=self.ACCENT_COLOR, 
                                          selectforeground=self.TEXT_COLOR,
                                          normalbackground=self.DATE_ENTRY_FIELD_BG, 
                                          normalforeground=self.TEXT_COLOR,     
                                          headersbackground=self.ACCENT_COLOR,
                                          headersforeground=self.TEXT_COLOR,
                                          disabledbackground=self.CARD_COLOR, # For consistency if DateEntry itself is disabled
                                          disabledforeground=self.SECONDARY_TEXT_COLOR
                                          ) 
        self.start_date_entry.pack(pady=5, padx=20, fill="x")
        self.start_date_entry.bind("<<DateEntrySelected>>", self.on_date_selected)

        ctk.CTkLabel(self.billing_cycle_card, text="End Date:", font=self.app_font, text_color=self.SECONDARY_TEXT_COLOR).pack(anchor="w", padx=20, pady=(10,0))
        self.end_date_entry = DateEntry(self.billing_cycle_card, width=18, 
                                        date_pattern='yyyy-mm-dd',
                                        font=self.app_font,
                                        background=self.ACCENT_COLOR, 
                                        foreground=self.TEXT_COLOR,   
                                        bordercolor=self.BORDER_COLOR,
                                        selectbackground=self.ACCENT_COLOR,
                                        selectforeground=self.TEXT_COLOR,
                                        normalbackground=self.DATE_ENTRY_FIELD_BG,
                                        normalforeground=self.TEXT_COLOR,
                                        headersbackground=self.ACCENT_COLOR,
                                        headersforeground=self.TEXT_COLOR,
                                        disabledbackground=self.CARD_COLOR,
                                        disabledforeground=self.SECONDARY_TEXT_COLOR
                                        )
        self.end_date_entry.pack(pady=5, padx=20, fill="x")
        self.end_date_entry.bind("<<DateEntrySelected>>", self.on_date_selected)

        self.date_error_label = ctk.CTkLabel(self.billing_cycle_card, text="", text_color=self.ERROR_COLOR, font=self.small_font)
        self.date_error_label.pack(pady=(5,15), padx=20)

    def on_date_selected(self, event=None):
        self.validate_dates()
        self.update_conditional_cards()
        self.check_all_inputs_for_calc_button()

    def validate_dates(self):
        try:
            start_date = self.start_date_entry.get_date()
            end_date = self.end_date_entry.get_date()

            if end_date < start_date:
                self.date_error_label.configure(text="End Date cannot be before Start Date.")
                if hasattr(self, 'reading_start_entry'): self.reading_start_entry.configure(state="disabled")
                if hasattr(self, 'reading_end_entry'): self.reading_end_entry.configure(state="disabled")
                return False
            else:
                self.date_error_label.configure(text="")
                if hasattr(self, 'reading_start_entry'): self.reading_start_entry.configure(state="normal")
                if hasattr(self, 'reading_end_entry'): self.reading_end_entry.configure(state="normal")
                self.start_date_val = start_date
                self.end_date_val = end_date
                if hasattr(self, 'reading_start_label'): self.reading_start_label.configure(text=f"Reading on {start_date.strftime('%Y-%m-%d')}:")
                if hasattr(self, 'reading_end_label'): self.reading_end_label.configure(text=f"Reading on {end_date.strftime('%Y-%m-%d')}:")
                return True
        except Exception:
            if hasattr(self, 'reading_start_entry'): self.reading_start_entry.configure(state="disabled")
            if hasattr(self, 'reading_end_entry'): self.reading_end_entry.configure(state="disabled")
            return False

    def create_meter_readings_card(self):
        self.meter_readings_card = self.create_styled_card(self.main_container)
        ctk.CTkLabel(self.meter_readings_card, text="🕵️‍♂️ X's AC Meter Readings", font=self.header_font, text_color=self.TEXT_COLOR).pack(pady=(15,10), padx=20, anchor="w")

        self.reading_start_label = ctk.CTkLabel(self.meter_readings_card, text="Reading on [Start Date]:", font=self.app_font, text_color=self.SECONDARY_TEXT_COLOR)
        self.reading_start_label.pack(anchor="w", padx=20, pady=(5,0))
        self.reading_start_entry = ctk.CTkEntry(self.meter_readings_card, placeholder_text="Enter KWH", font=self.app_font, state="disabled", 
                                                border_color=self.BORDER_COLOR, fg_color=self.CARD_COLOR, text_color=self.TEXT_COLOR,
                                                placeholder_text_color=self.SECONDARY_TEXT_COLOR)
        self.reading_start_entry.pack(pady=5, padx=20, fill="x")
        self.reading_start_entry.bind("<KeyRelease>", self.check_all_inputs_for_calc_button)

        self.reading_end_label = ctk.CTkLabel(self.meter_readings_card, text="Reading on [End Date]:", font=self.app_font, text_color=self.SECONDARY_TEXT_COLOR)
        self.reading_end_label.pack(anchor="w", padx=20, pady=(10,0))
        self.reading_end_entry = ctk.CTkEntry(self.meter_readings_card, placeholder_text="Enter KWH", font=self.app_font, state="disabled", 
                                              border_color=self.BORDER_COLOR, fg_color=self.CARD_COLOR, text_color=self.TEXT_COLOR,
                                              placeholder_text_color=self.SECONDARY_TEXT_COLOR)
        self.reading_end_entry.pack(pady=5, padx=20, fill="x")
        self.reading_end_entry.bind("<KeyRelease>", self.check_all_inputs_for_calc_button)

        self.reading_error_label = ctk.CTkLabel(self.meter_readings_card, text="", text_color=self.ERROR_COLOR, font=self.small_font)
        self.reading_error_label.pack(pady=(5,15), padx=20)

    def create_monthly_details_cards_container(self):
        self.monthly_details_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.monthly_details_container.pack(pady=0, padx=0, fill="x")
        self.single_month_details_card = None
        self.multi_month_segment1_card = None

    def update_conditional_cards(self):
        if self.single_month_details_card: self.single_month_details_card.destroy(); self.single_month_details_card = None
        if self.multi_month_segment1_card: self.multi_month_segment1_card.destroy(); self.multi_month_segment1_card = None

        if not hasattr(self, 'start_date_val') or not hasattr(self, 'end_date_val'): return

        start_date, end_date = self.start_date_val, self.end_date_val

        if start_date.year == end_date.year and start_date.month == end_date.month:
            self.single_month_details_card = self.create_styled_card(self.monthly_details_container)
            month_name = start_date.strftime('%B %Y')
            ctk.CTkLabel(self.single_month_details_card, text=f"💡 Details for {month_name}", font=self.header_font, text_color=self.TEXT_COLOR).pack(pady=(15,10), padx=20, anchor="w")
            ctk.CTkLabel(self.single_month_details_card, text=f"KWH X already used in {start_date.strftime('%B')} *before* {start_date.strftime('%Y-%m-%d')}?", font=self.app_font, text_color=self.SECONDARY_TEXT_COLOR).pack(anchor="w", padx=20, pady=(5,0))
            self.kwh_offset_month1_entry = ctk.CTkEntry(self.single_month_details_card, placeholder_text="0 (if none)", font=self.app_font, 
                                                        border_color=self.BORDER_COLOR, fg_color=self.CARD_COLOR, text_color=self.TEXT_COLOR,
                                                        placeholder_text_color=self.SECONDARY_TEXT_COLOR)
            self.kwh_offset_month1_entry.pack(pady=5, padx=20, fill="x")
            self.kwh_offset_month1_entry.bind("<KeyRelease>", self.check_all_inputs_for_calc_button)
            ctk.CTkLabel(self.single_month_details_card, text="Enter 0 if this is the first usage in the month.", font=self.small_font, text_color=self.SECONDARY_TEXT_COLOR).pack(anchor="w", padx=20, pady=(5,15))
        else:
            self.multi_month_segment1_card = self.create_styled_card(self.monthly_details_container)
            month1_name = start_date.strftime('%B %Y')
            ctk.CTkLabel(self.multi_month_segment1_card, text=f"💡 Segment 1: {month1_name}", font=self.header_font, text_color=self.TEXT_COLOR).pack(pady=(15,5), padx=20, anchor="w")
            ctk.CTkLabel(self.multi_month_segment1_card, text=f"(Covers {start_date.strftime('%Y-%m-%d')} to end of {start_date.strftime('%B')})", font=self.small_font, text_color=self.SECONDARY_TEXT_COLOR).pack(anchor="w", padx=20, pady=(0,10))
            
            ctk.CTkLabel(self.multi_month_segment1_card, text=f"KWH X already used in {start_date.strftime('%B')} *before* {start_date.strftime('%Y-%m-%d')}?", font=self.app_font, text_color=self.SECONDARY_TEXT_COLOR).pack(anchor="w", padx=20, pady=(5,0))
            self.kwh_offset_month1_entry = ctk.CTkEntry(self.multi_month_segment1_card, placeholder_text="0 (if none)", font=self.app_font, 
                                                        border_color=self.BORDER_COLOR, fg_color=self.CARD_COLOR, text_color=self.TEXT_COLOR,
                                                        placeholder_text_color=self.SECONDARY_TEXT_COLOR)
            self.kwh_offset_month1_entry.pack(pady=5, padx=20, fill="x")
            self.kwh_offset_month1_entry.bind("<KeyRelease>", self.check_all_inputs_for_calc_button)

            if start_date.month == 12: self.month2_start_date_val = datetime.date(start_date.year + 1, 1, 1)
            else: self.month2_start_date_val = datetime.date(start_date.year, start_date.month + 1, 1)
            
            ctk.CTkLabel(self.multi_month_segment1_card, text=f"Meter reading on {self.month2_start_date_val.strftime('%Y-%m-%d')} (start of {self.month2_start_date_val.strftime('%B')}):", font=self.app_font, text_color=self.SECONDARY_TEXT_COLOR).pack(anchor="w", padx=20, pady=(10,0))
            self.reading_month2_start_entry = ctk.CTkEntry(self.multi_month_segment1_card, placeholder_text="Enter KWH", font=self.app_font, 
                                                           border_color=self.BORDER_COLOR, fg_color=self.CARD_COLOR, text_color=self.TEXT_COLOR,
                                                           placeholder_text_color=self.SECONDARY_TEXT_COLOR)
            self.reading_month2_start_entry.pack(pady=5, padx=20, fill="x")
            self.reading_month2_start_entry.bind("<KeyRelease>", self.check_all_inputs_for_calc_button)
            self.intermediate_reading_error_label = ctk.CTkLabel(self.multi_month_segment1_card, text="", text_color=self.ERROR_COLOR, font=self.small_font)
            self.intermediate_reading_error_label.pack(pady=(5,10), padx=20)

            month2_name = self.month2_start_date_val.strftime('%B %Y')
            ctk.CTkLabel(self.multi_month_segment1_card, text=f"✨ Segment 2: {month2_name} (from {self.month2_start_date_val.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})", font=self.header_font, text_color=self.TEXT_COLOR).pack(pady=(10,5), padx=20, anchor="w")
            ctk.CTkLabel(self.multi_month_segment1_card, text="KWH for tiering resets. No offset needed for segment 2.", font=self.small_font, text_color=self.SECONDARY_TEXT_COLOR).pack(anchor="w", padx=20, pady=(0,15))
        self.check_all_inputs_for_calc_button()

    def create_calculate_button(self):
        self.calculate_button = ctk.CTkButton(self.main_container, text="CALCULATE X's SHARE 💸", font=self.header_font, 
                                              command=self.perform_calculation, fg_color=self.ACCENT_COLOR,
                                              hover_color=self.ACCENT_HOVER_COLOR, 
                                              text_color=self.TEXT_COLOR, 
                                              height=45, corner_radius=10) 
        self.calculate_button.pack(pady=25, padx=5, fill="x") 

    def create_results_card(self):
        self.results_card = self.create_styled_card(self.main_container) 
        ctk.CTkLabel(self.results_card, text="📊 The Bill Breakdown for X", font=self.header_font, text_color=self.TEXT_COLOR).pack(pady=(15,10), padx=20, anchor="w")
        
        self.results_period_label = ctk.CTkLabel(self.results_card, text="Period: ", font=self.app_font, text_color=self.SECONDARY_TEXT_COLOR)
        self.results_period_label.pack(anchor="w", padx=20, pady=(5,0))
        
        # Frame for Month 1 details
        self.month1_results_frame = ctk.CTkFrame(self.results_card, fg_color="transparent")
        self.month1_results_frame.pack(fill="x", padx=20, pady=5)
        self.segment1_details_label = ctk.CTkLabel(self.month1_results_frame, text="", justify="left", font=self.app_font, text_color=self.TEXT_COLOR, wraplength=600)
        self.segment1_details_label.pack(anchor="w")

        # Frame for Month 2 details (optional)
        self.month2_results_frame = ctk.CTkFrame(self.results_card, fg_color="transparent")
        # self.month2_results_frame will be packed in perform_calculation if needed
        self.segment2_details_label = ctk.CTkLabel(self.month2_results_frame, text="", justify="left", font=self.app_font, text_color=self.TEXT_COLOR, wraplength=600)
        self.segment2_details_label.pack(anchor="w")
        
        separator = ctk.CTkFrame(self.results_card, height=1, fg_color=self.BORDER_COLOR) 
        separator.pack(fill="x", padx=20, pady=10)
        
        self.total_cost_for_period_label = ctk.CTkLabel(self.results_card, text="TOTAL for Period: BDT", font=self.result_font, text_color=self.ACCENT_COLOR)
        self.total_cost_for_period_label.pack(pady=(5,10), padx=20, anchor="w")

        self.results_note_label = ctk.CTkLabel(self.results_card, text="", justify="left", font=self.small_font, text_color=self.SECONDARY_TEXT_COLOR, wraplength=600)
        self.results_note_label.pack(anchor="w", padx=20, pady=(0,15))
        
        self.calculation_error_label = ctk.CTkLabel(self.results_card, text="", text_color=self.ERROR_COLOR, font=self.small_font)
        self.calculation_error_label.pack(pady=(0,15), padx=20, anchor="w")


    def create_y_context_card(self):
        self.y_context_card = self.create_styled_card(self.main_container) 
        
        header_frame = ctk.CTkFrame(self.y_context_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15,5))
        ctk.CTkLabel(header_frame, text="🤔 What About Y? (Optional)", font=self.header_font, text_color=self.TEXT_COLOR).pack(side="left")
        self.y_toggle_switch = ctk.CTkSwitch(header_frame, text="", command=self.toggle_y_details, 
                                             variable=ctk.StringVar(value="off"), onvalue="on", offvalue="off",
                                             progress_color=self.ACCENT_COLOR, button_color=self.ACCENT_COLOR,
                                             button_hover_color=self.ACCENT_HOVER_COLOR)
        self.y_toggle_switch.pack(side="left", padx=10)

        self.y_details_frame = ctk.CTkFrame(self.y_context_card, fg_color="transparent") 
        
        ctk.CTkLabel(self.y_details_frame, text="Total amount Y paid to utility for this period?", font=self.app_font, text_color=self.SECONDARY_TEXT_COLOR).pack(anchor="w", padx=20, pady=(10,0))
        self.y_paid_entry = ctk.CTkEntry(self.y_details_frame, placeholder_text="Enter BDT", font=self.app_font, 
                                         border_color=self.BORDER_COLOR, fg_color=self.CARD_COLOR, text_color=self.TEXT_COLOR,
                                         placeholder_text_color=self.SECONDARY_TEXT_COLOR)
        self.y_paid_entry.pack(pady=5, padx=20, fill="x")
        self.y_net_cost_button = ctk.CTkButton(self.y_details_frame, text="CALCULATE Y's NET COST", font=self.app_font, 
                                               command=self.calculate_y_net_cost, fg_color=self.ACCENT_COLOR,
                                               hover_color=self.ACCENT_HOVER_COLOR, 
                                               text_color=self.TEXT_COLOR,
                                               height=35, corner_radius=8)
        self.y_net_cost_button.pack(pady=10, padx=20, fill="x")
        self.y_net_cost_label = ctk.CTkLabel(self.y_details_frame, text="Y's Effective Utility Cost: BDT", font=self.result_font, text_color=self.ACCENT_COLOR) # Changed to ACCENT_COLOR for Y's cost too
        self.y_net_cost_label.pack(pady=5, padx=20, anchor="w")
        self.y_error_label = ctk.CTkLabel(self.y_details_frame, text="", text_color=self.ERROR_COLOR, font=self.small_font)
        self.y_error_label.pack(pady=(5,15), padx=20, anchor="w")

    def toggle_y_details(self):
        if self.y_toggle_switch.get() == "on": self.y_details_frame.pack(fill="x", pady=(0,10), padx=0) 
        else:
            self.y_details_frame.pack_forget()
            self.y_paid_entry.delete(0, ctk.END)
            self.y_net_cost_label.configure(text="Y's Effective Utility Cost: BDT") # Reset text
            self.y_error_label.configure(text="")

    def get_float_input_gui(self, entry_widget, error_label_widget, field_name="Value"):
        try:
            val_str = entry_widget.get()
            if not val_str: error_label_widget.configure(text=f"{field_name} cannot be empty."); return None # Added check for empty
            val = float(val_str)
            if val < 0: error_label_widget.configure(text=f"{field_name} cannot be negative."); return None
            error_label_widget.configure(text="")
            return val
        except ValueError: error_label_widget.configure(text=f"Invalid input for {field_name}. Please enter a number."); return None

    def check_all_inputs_for_calc_button(self, event=None):
        self.calculate_button.configure(state="disabled") 

        if not self.validate_dates(): return

        if not (hasattr(self, 'reading_start_entry') and self.reading_start_entry.cget("state") == "normal"):
            return

        start_reading_str = self.reading_start_entry.get()
        end_reading_str = self.reading_end_entry.get()
        if not start_reading_str or not end_reading_str: return
        try:
            float(start_reading_str); float(end_reading_str)
        except ValueError: return

        is_single_month_active = hasattr(self, 'single_month_details_card') and self.single_month_details_card is not None and self.single_month_details_card.winfo_exists()
        is_multi_month_active = hasattr(self, 'multi_month_segment1_card') and self.multi_month_segment1_card is not None and self.multi_month_segment1_card.winfo_exists()

        if is_single_month_active:
            if not (hasattr(self, 'kwh_offset_month1_entry') and self.kwh_offset_month1_entry.get()): return
            try: float(self.kwh_offset_month1_entry.get())
            except ValueError: return
        elif is_multi_month_active:
            if not (hasattr(self, 'kwh_offset_month1_entry') and self.kwh_offset_month1_entry.get() and \
                    hasattr(self, 'reading_month2_start_entry') and self.reading_month2_start_entry.get()): return
            try:
                float(self.kwh_offset_month1_entry.get()); float(self.reading_month2_start_entry.get())
            except ValueError: return
        elif (hasattr(self, 'start_date_val') and hasattr(self, 'end_date_val')) and not is_single_month_active and not is_multi_month_active:
             # This case means dates are valid, but conditional cards haven't appeared yet.
             # This can happen if on_date_selected is called before update_conditional_cards fully processes.
             # Keep button disabled until month type is determined and its fields are ready.
            return
        self.calculate_button.configure(state="normal")

    def perform_calculation(self):
        # Reset previous results and errors
        self.results_card.pack_forget()
        self.y_context_card.pack_forget()
        self.month1_results_frame.pack_forget() # Ensure it's hidden before repacking
        self.month2_results_frame.pack_forget() # Ensure it's hidden
        self.calculation_error_label.configure(text="")
        self.segment1_details_label.configure(text="")
        self.segment2_details_label.configure(text="")
        self.total_cost_for_period_label.configure(text="TOTAL for Period: BDT")
        self.results_note_label.configure(text="")


        if not self.validate_dates():
            self.calculation_error_label.configure(text="Please fix date errors.")
            self.results_card.pack(pady=12, padx=5, fill="x"); return 

        start_date, end_date = self.start_date_val, self.end_date_val
        reading_on_start_date = self.get_float_input_gui(self.reading_start_entry, self.reading_error_label, "Start Reading")
        reading_on_end_date = self.get_float_input_gui(self.reading_end_entry, self.reading_error_label, "End Reading")

        if reading_on_start_date is None or reading_on_end_date is None:
            self.calculation_error_label.configure(text="Please fix meter reading errors.")
            self.results_card.pack(pady=12, padx=5, fill="x"); return
        if reading_on_end_date < reading_on_start_date:
            self.reading_error_label.configure(text="End reading cannot be less than start reading.")
            self.calculation_error_label.configure(text="Please fix meter reading errors.")
            self.results_card.pack(pady=12, padx=5, fill="x"); return
        else: self.reading_error_label.configure(text="")

        overall_total_cost_for_x_period = 0
        cost_for_month1_segment = 0
        cost_for_month2_segment = 0 # Initialize for multi-month case

        is_single_month_active = hasattr(self, 'single_month_details_card') and self.single_month_details_card is not None and self.single_month_details_card.winfo_exists()
        is_multi_month_active = hasattr(self, 'multi_month_segment1_card') and self.multi_month_segment1_card is not None and self.multi_month_segment1_card.winfo_exists()

        # Display results period
        self.results_period_label.configure(text=f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        self.month1_results_frame.pack(fill="x", pady=(5,0)) # Pack month 1 frame

        if is_single_month_active:
            kwh_offset_month1 = self.get_float_input_gui(self.kwh_offset_month1_entry, self.calculation_error_label, "KWH Offset")
            if kwh_offset_month1 is None: self.results_card.pack(pady=12, padx=5, fill="x"); return
            
            kwh_in_period_segment = round(reading_on_end_date - reading_on_start_date, 2)
            
            cost_for_month1_segment, rate_m1, total_kwh_for_rate_calc_m1, err_m1 = calculate_tiered_cost_for_x(kwh_in_period_segment, kwh_offset_month1)
            if err_m1:
                self.calculation_error_label.configure(text=err_m1); self.results_card.pack(pady=12, padx=5, fill="x"); return

            overall_total_cost_for_x_period = cost_for_month1_segment
            
            segment1_text = (f"--- {start_date.strftime('%B %Y')} ---\n"
                             f"  KWH in this period: {kwh_in_period_segment:.2f} KWH\n"
                             f"  Total KWH for rate (incl. offset): {total_kwh_for_rate_calc_m1:.2f} KWH\n"
                             f"  Slab rate applied: {rate_m1:.2f} BDT/KWH\n"
                             f"  Accumulated cost for {start_date.strftime('%B %Y')} (up to {end_date.strftime('%Y-%m-%d')}): {cost_for_month1_segment:.2f} BDT")
            self.segment1_details_label.configure(text=segment1_text)
            self.results_note_label.configure(text=f"(This represents the total value of X's consumption in {start_date.strftime('%B %Y')} up to {end_date.strftime('%Y-%m-%d')}. Adjust for any prior payments made by X for this month's AC use.)")

        elif is_multi_month_active:
            kwh_offset_month1 = self.get_float_input_gui(self.kwh_offset_month1_entry, self.calculation_error_label, "Month 1 KWH Offset")
            reading_on_month2_start = self.get_float_input_gui(self.reading_month2_start_entry, self.intermediate_reading_error_label, "Intermediate Reading")
            
            if kwh_offset_month1 is None or reading_on_month2_start is None:
                self.calculation_error_label.configure(text="Fix KWH offset or intermediate reading errors.")
                self.results_card.pack(pady=12, padx=5, fill="x"); return
            if not (reading_on_start_date <= reading_on_month2_start <= reading_on_end_date):
                self.intermediate_reading_error_label.configure(text="Intermediate reading must be between start/end readings.")
                self.calculation_error_label.configure(text="Fix intermediate reading error.")
                self.results_card.pack(pady=12, padx=5, fill="x"); return
            else: self.intermediate_reading_error_label.configure(text="")

            # Month 1 Segment Calculation
            kwh_in_month1_segment = round(reading_on_month2_start - reading_on_start_date, 2)
            cost_for_month1_segment, rate_m1, total_kwh_for_rate_calc_m1, err_m1 = calculate_tiered_cost_for_x(kwh_in_month1_segment, kwh_offset_month1)
            if err_m1:
                self.calculation_error_label.configure(text=f"Month 1: {err_m1}"); self.results_card.pack(pady=12, padx=5, fill="x"); return
            
            segment1_text = (f"--- {start_date.strftime('%B %Y')} (Portion: {start_date.strftime('%d')} to {self.month2_start_date_val.day -1 if self.month2_start_date_val.day > 1 else start_date.replace(day=1).strftime('%d')}) ---\n" # Approximation of end day
                             f"  KWH in segment: {kwh_in_month1_segment:.2f} KWH\n"
                             f"  Total KWH for rate (incl. offset): {total_kwh_for_rate_calc_m1:.2f} KWH\n"
                             f"  Slab rate applied: {rate_m1:.2f} BDT/KWH\n"
                             f"  Accumulated cost for {start_date.strftime('%B %Y')} (up to end of month): {cost_for_month1_segment:.2f} BDT")
            self.segment1_details_label.configure(text=segment1_text)

            # Month 2 Segment Calculation
            kwh_in_month2_segment = round(reading_on_end_date - reading_on_month2_start, 2)
            cost_for_month2_segment, rate_m2, total_kwh_for_rate_calc_m2, err_m2 = calculate_tiered_cost_for_x(kwh_in_month2_segment, 0) # Offset is 0 for month 2
            if err_m2:
                self.calculation_error_label.configure(text=f"Month 2: {err_m2}"); self.results_card.pack(pady=12, padx=5, fill="x"); return

            self.month2_results_frame.pack(fill="x", padx=20, pady=5) # Pack month 2 frame
            segment2_text = (f"--- {self.month2_start_date_val.strftime('%B %Y')} (Portion: {self.month2_start_date_val.strftime('%d')} to {end_date.strftime('%d')}) ---\n"
                             f"  KWH in segment: {kwh_in_month2_segment:.2f} KWH\n"
                             f"  Total KWH for rate: {total_kwh_for_rate_calc_m2:.2f} KWH\n"
                             f"  Slab rate applied: {rate_m2:.2f} BDT/KWH\n"
                             f"  Accumulated cost for {self.month2_start_date_val.strftime('%B %Y')} (up to {end_date.strftime('%Y-%m-%d')}): {cost_for_month2_segment:.2f} BDT")
            self.segment2_details_label.configure(text=segment2_text)
            
            # The overall total for the period is the sum of the costs of the two segments.
            # The backend's main() function sums cost_month1 and cost_month2.
            # Here, cost_for_month1_segment and cost_for_month2_segment are the values of consumption in those segments.
            overall_total_cost_for_x_period = round(cost_for_month1_segment + cost_for_month2_segment, 2)
            self.results_note_label.configure(text=f"(The amounts for each month represent the total value of X's consumption in that month's portion of the period. Adjust for any prior payments made by X for AC use in those respective months.)")


        else: 
            self.calculation_error_label.configure(text="Error: Could not determine calculation period type. Please check dates.")
            self.results_card.pack(pady=12, padx=5, fill="x"); return

        self.total_cost_for_period_label.configure(text=f"TOTAL for Period ({start_date.strftime('%d %b')} - {end_date.strftime('%d %b %Y')}): {overall_total_cost_for_x_period:.2f} BDT")
        self.results_card.pack(pady=12, padx=5, fill="x") 
        self.total_x_cost_for_y_calc = overall_total_cost_for_x_period # For Y's calculation
        self.y_context_card.pack(pady=12, padx=5, fill="x") 
        if self.y_toggle_switch.get() == "off": self.y_details_frame.pack_forget()

    def calculate_y_net_cost(self):
        self.y_error_label.configure(text="")
        if not hasattr(self, 'total_x_cost_for_y_calc'): # Check if X's cost has been calculated
            self.y_error_label.configure(text="Calculate X's share first."); return
        
        total_recharge_by_y_str = self.y_paid_entry.get()
        if not total_recharge_by_y_str: # Check if Y's payment field is empty
             self.y_error_label.configure(text="Enter Total Recharge Amount Y paid."); return

        total_recharge_by_y = self.get_float_input_gui(self.y_paid_entry, self.y_error_label, "Y's Payment")
        if total_recharge_by_y is None: return # Error already set by get_float_input_gui

        y_net_cost = round(total_recharge_by_y - self.total_x_cost_for_y_calc, 2)
        self.y_net_cost_label.configure(text=f"Y's Effective Utility Cost: {y_net_cost:.2f} BDT")

if __name__ == "__main__":
    app = ACBillSplitterApp()
    app.mainloop()
