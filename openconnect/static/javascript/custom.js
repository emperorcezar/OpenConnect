function customIsValid(/*Boolean*/ isFocused){
    // summary: Only fires validator on blur OR if the field has already been marked as invalid
    // description: 
    //      This allows the user to type without getting an invalid message
    //       until the field is no longer focused. When the user returns to a
    //       field with an error, validation will occur onKeyUp until the field is
    //       valid again
    
    var skipValidator = isFocused;
				     
    if(this.state == "Error"){
	// If  the error state is already set, do not skip the validator
	skipValidator = false;
    }
    
    return skipValidator || this.validator(this.textbox.value, this.constraints);
}
				     