"""
TextEngine: A Gap Buffer Implementation for Efficient Text Editing

This class implements a "gap buffer" data structure, which is commonly used in text editors
for efficient insertion and deletion operations. The gap buffer maintains a contiguous block
of memory (a list in Python) with an empty "gap" that follows the cursor position.

Key Concepts:
- The buffer is a list with a gap (empty space) in the middle
- Text before the gap: buffer[0:gap_start]
- The gap itself: buffer[gap_start:gap_end] (contains None values)
- Text after the gap: buffer[gap_end:]
- When inserting text, we fill the gap from left to right
- When moving the cursor, we move the gap to follow it

Example buffer state with text "Hello World" and cursor after "Hello":
[H][e][l][l][o][None][None][None][ ][W][o][r][l][d]
                ^gap_start          ^gap_end
"""


class TextEngine:
    """
    A text editor engine using the gap buffer algorithm for efficient editing operations.
    
    The gap buffer provides O(1) insertion at the cursor position by maintaining
    an empty gap that moves with the cursor. This is much more efficient than
    repeatedly inserting into a standard list, which requires shifting all
    subsequent elements.
    """
    
    def __init__(self, initial_capacity=100):
        """
        Initialize a new TextEngine with an empty gap buffer.
        
        Parameters:
        -----------
        initial_capacity : int, optional (default=100)
            The initial size of the buffer array. This determines how many
            characters can be stored before the buffer needs to be resized.
        
        Attributes:
        -----------
        self.buffer : list
            The main storage array containing both text characters and None values
            representing the gap. Initially filled entirely with None.
            
        self.gap_start : int
            Index pointing to the start of the gap (where new characters will be inserted).
            This represents the cursor position in the text.
            
        self.gap_end : int
            Index pointing to the end of the gap (one past the last None in the gap).
            Text after the cursor starts at this position.
        
        Initial State:
        -------------
        buffer = [None, None, None, ..., None]  (length = initial_capacity)
        gap_start = 0
        gap_end = initial_capacity
        (The entire buffer is initially a gap, ready for text insertion)
        """
        # Create a buffer filled with None values to represent empty space
        self.buffer = [None] * initial_capacity
        
        # Gap starts at the beginning (cursor at position 0)
        self.gap_start = 0
        
        # Gap ends at the end of the buffer (entire buffer is empty initially)
        self.gap_end = initial_capacity

    def insert_char(self, char):
        """
        Insert a single character at the current cursor position (gap_start).
        
        This operation is O(1) when there's space in the gap, making it very efficient
        for sequential typing. The character is placed at gap_start, and gap_start
        is incremented, effectively shrinking the gap from the left.
        
        Parameters:
        -----------
        char : str
            A single character to insert at the cursor position.
        
        Algorithm:
        ----------
        1. Check if gap has space (gap_start < gap_end)
        2. If no space, print error message (resize not implemented)
        3. If space available:
           - Place character at gap_start position
           - Increment gap_start to move cursor forward
        
        Example:
        --------
        Before inserting 'A' with gap_start=0, gap_end=3:
        [None][None][None]
         ^gap_start       ^gap_end
        
        After inserting 'A':
        [A][None][None]
            ^gap_start  ^gap_end
        
        Returns:
        --------
        None
        """
        # Check if the gap has been completely filled (no more space)
        # When gap_start == gap_end, there's no gap left to insert into
        if self.gap_start == self.gap_end:
            # Buffer is full - in a complete implementation, we would resize here
            # TODO: Implement _resize() method to expand the buffer capacity
            print("Buffer Full! (Resize not implemented yet)") 
            return  # Exit without inserting
        
        # Place the character at the current gap_start position
        # This fills one position of the gap with actual text
        self.buffer[self.gap_start] = char
        
        # Move gap_start forward by one position
        # This effectively moves the cursor forward and shrinks the gap from the left
        self.gap_start += 1

    def set_cursor(self, new_pos):
        """
        Move the cursor (and the gap) to a new position in the text.
        
        This is the most complex operation in the gap buffer. When moving the cursor,
        we must also move the gap to follow it. This involves copying characters
        from one side of the gap to the other, effectively "sliding" the gap through
        the buffer.
        
        Parameters:
        -----------
        new_pos : int
            The desired cursor position (0-based index in the logical text).
            Position 0 means before the first character.
            Position n means after the nth character.
        
        Algorithm Overview:
        -------------------
        1. Calculate the actual text length (excluding the gap)
        2. Clamp new_pos to valid range [0, text_length]
        3. If gap needs to move left: copy characters from left to right
        4. If gap needs to move right: copy characters from right to left
        
        Time Complexity:
        ----------------
        O(d) where d is the distance moved. This is why gap buffers are efficient
        for local editing but slower for jumping to distant positions.
        
        Example - Moving gap LEFT:
        --------------------------
        Before (cursor at position 3, want to move to position 1):
        [H][e][l][None][None][W][o][r][l][d]
                   ^gap_start      ^gap_end
        
        After moving left to position 1:
        [H][None][None][e][l][W][o][r][l][d]
            ^gap_start         ^gap_end
        
        Example - Moving gap RIGHT:
        ---------------------------
        Before (cursor at position 1, want to move to position 3):
        [H][None][None][e][l][W][o][r][l][d]
            ^gap_start         ^gap_end
        
        After moving right to position 3:
        [H][e][l][None][None][W][o][r][l][d]
                   ^gap_start      ^gap_end
        """
        # Calculate the current length of actual text (not including the gap)
        # Formula: total_buffer_size - gap_size
        # gap_size = gap_end - gap_start
        current_text_length = len(self.buffer) - (self.gap_end - self.gap_start)
        
        # Clamp new_pos to valid range to prevent out-of-bounds errors
        # max(0, ...) ensures position isn't negative
        # min(..., current_text_length) ensures position isn't beyond the text
        new_pos = max(0, min(new_pos, current_text_length))

        # MOVING GAP LEFT (cursor moving backward/left in the text)
        # ---------------------------------------------------------
        # When gap_start > new_pos, we need to move the gap leftward
        # We do this by:
        # 1. Copying a character from just before gap_start to just before gap_end
        # 2. Moving both gap_start and gap_end one position left
        # 3. Repeating until gap_start reaches new_pos
        while self.gap_start > new_pos:
            # Move gap_start back by one position
            self.gap_start -= 1
            
            # Move gap_end back by one position (gap size stays constant)
            self.gap_end -= 1
            
            # Copy the character that was at gap_start to the gap_end position
            # This effectively moves the character from left side to right side of gap
            self.buffer[self.gap_end] = self.buffer[self.gap_start]
            
            # Clear the old position (set to None) to maintain gap integrity
            self.buffer[self.gap_start] = None 

        # MOVING GAP RIGHT (cursor moving forward/right in the text)
        # -----------------------------------------------------------
        # When gap_start < new_pos, we need to move the gap rightward
        # We do this by:
        # 1. Copying a character from gap_end to gap_start
        # 2. Moving both gap_start and gap_end one position right
        # 3. Repeating until gap_start reaches new_pos
        while self.gap_start < new_pos:
            # Copy the character at gap_end to the gap_start position
            # This effectively moves the character from right side to left side of gap
            self.buffer[self.gap_start] = self.buffer[self.gap_end]
            
            # Clear the old position (set to None) to maintain gap integrity
            self.buffer[self.gap_end] = None 
            
            # Move gap_start forward by one position
            self.gap_start += 1
            
            # Move gap_end forward by one position (gap size stays constant)
            self.gap_end += 1

    def get_text(self):
        """
        Retrieve the complete text from the buffer as a single string.
        
        This method reconstructs the actual text by concatenating the parts
        before and after the gap, while excluding the gap itself (None values).
        
        Algorithm:
        ----------
        1. Extract the prefix (text before the gap): buffer[0:gap_start]
        2. Extract the suffix (text after the gap): buffer[gap_end:]
        3. Filter out any None values (defensive programming)
        4. Join all characters into a single string
        
        Returns:
        --------
        str
            The complete text content without the gap, as a single string.
        
        Example:
        --------
        Buffer state: [H][e][l][None][None][l][o]
                                 ^gap_start   ^gap_end
        
        prefix = [H][e][l]
        suffix = [l][o]
        result = "Hello"
        
        Time Complexity:
        ----------------
        O(n) where n is the buffer size, as we must examine all elements
        """
        # Get all characters before the gap (from index 0 to gap_start, exclusive)
        # These are the characters already typed up to the cursor position
        prefix = self.buffer[:self.gap_start]
        
        # Get all characters after the gap (from gap_end to end of buffer)
        # These are the characters that come after the cursor position
        suffix = self.buffer[self.gap_end:]
        
        # Filter out any None values from the prefix
        # In normal operation, prefix should not contain None, but this is
        # defensive programming to ensure we only get actual characters
        clean_prefix = [c for c in prefix if c is not None]
        
        # Filter out any None values from the suffix
        # Same defensive measure as above
        clean_suffix = [c for c in suffix if c is not None]
        
        # Combine the prefix and suffix lists, then join all characters into a string
        # The join() method concatenates all list elements with an empty string separator
        return "".join(clean_prefix + clean_suffix)

    def __repr__(self):
        """
        Return a string representation of the TextEngine for debugging purposes.
        
        This special method is called when you use repr() or print() on a TextEngine
        object. It provides a view of the internal buffer state and gap boundaries,
        which is useful for understanding how the gap buffer is working.
        
        Returns:
        --------
        str
            A multi-line string showing:
            - The complete buffer array with all elements
            - The current gap boundaries (gap_start and gap_end indices)
        
        Example Output:
        ---------------
        Buffer: ['H', 'e', 'l', None, None, 'l', 'o']
        Gap: [3:5]
        
        This shows the text "Hello" with a gap between indices 3 and 5.
        """
        # Use an f-string (formatted string literal) to create the representation
        # \n creates a newline character for multi-line output
        # self.buffer shows the entire buffer list
        # [gap_start:gap_end] shows the range of indices occupied by the gap
        return f"Buffer: {self.buffer}\nGap: [{self.gap_start}:{self.gap_end}]"
    
    def delete_char(self):
        """
        Deletes the character immediately to the left of the cursor.
        """
        # If we are at the start of the file, do nothing
        if self.gap_start == 0:
            return

        # 1. Move the gap start back by one
        self.gap_start -= 1
        
        # 2. (Optional) Clear the data for debugging clarity
        self.buffer[self.gap_start] = None