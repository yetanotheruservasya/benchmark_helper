# Test Plan for Flask Application

This document outlines the test cases for the Flask application. The tests ensure that various endpoints and functionalities work correctly, including context management, message handling, and system prompts.

## Test Cases

### 1. `test_index`

**Description:**  
Verifies that the index page (`/`) loads correctly and contains key elements.

**Assertions:**
- The response status code is 200.
- The response contains the text "Set Context".
- The response contains the text "Save Context".

### 2. `test_save_context`

**Description:**  
Tests the `/save_context` endpoint to ensure that the context is saved correctly.

**Assertions:**
- The response status code is 200.
- The response JSON contains the `user_id` field with the correct value.
- The response JSON contains all expected context fields.
- Each context field has the correct value as provided in the request.

### 3. `test_openai_key`

**Description:**  
Checks that the OpenAI API key is set and valid by making a test request to the OpenAI API.

**Assertions:**
- The environment variable `OPENAI_API_KEY` is set.
- The OpenAI API request completes without errors and returns a valid response.

### 4. `test_handle_message`

**Description:**  
Tests message handling via Socket.IO by sending and receiving a message.

**Assertions:**
- The client connects to the room successfully.
- The message "Hello" is received by the client.

### 5. `test_handle_join_room`

**Description:**  
Tests the ability to join a room and verifies that the client receives a confirmation message.

**Assertions:**
- The client connects to the room successfully.
- The received events include a message indicating successful room join.

### 6. `test_save_user_history`

**Description:**  
Ensures that user message history is saved correctly to a JSON file.

**Assertions:**
- The history file exists.
- The history file contains the message "Test message".

### 7. `test_save_context_partial_fields`

**Description:**  
Tests saving context with partial fields to ensure defaults are applied where fields are missing.

**Assertions:**
- The response status code is 200.
- The response JSON contains the `user_id` and partially saved context.
- Fields not provided in the request are set to default values.

### 8. `test_save_context_no_user_id`

**Description:**  
Verifies that the absence of `user_id` in the request results in an error.

**Assertions:**
- The response status code is 400.
- The response JSON contains an error message indicating that `user_id` is required.

### 9. `test_save_user_history_multiple_messages`

**Description:**  
Checks that multiple messages are saved correctly to the user's history.

**Assertions:**
- The history file exists.
- The history file contains both "First message" and "Second message".

### 10. `test_join_multiple_rooms`

**Description:**  
Tests joining multiple rooms and ensures that the client receives join confirmations for both rooms.

**Assertions:**
- The client joins both `room1` and `room2`.
- The received events confirm successful joining of both rooms.

### 11. `test_join_room_no_room_name`

**Description:**  
Verifies that attempting to join a room without specifying a room name results in an error.

**Assertions:**
- The response includes an error message indicating that the room ID is required.

### 12. `test_handle_message_no_user_id`

**Description:**  
Tests sending a message without a `user_id` to verify proper error handling.

**Assertions:**
- The response includes an error message indicating that `user_id` is required or context not found.

### 13. `test_generate_system_prompt_full_context`

**Description:**  
Verifies that the `generate_system_prompt` function correctly incorporates all context data into the prompt.

**Assertions:**
- The generated prompt includes all provided context data.

### 14. `test_generate_system_prompt_invalid_context`

**Description:**  
Checks how `generate_system_prompt` handles context with invalid data types.

**Assertions:**
- The generated prompt includes all context data, converted to strings.