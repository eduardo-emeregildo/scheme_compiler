#will hold the functions for handling asm generation of global variables. Maybe turn this into a class if I need inheritance

from environment import *

ident_type_to_word = {
    IdentifierType.INT : "dq",
    IdentifierType.FLOAT : "dq",
    IdentifierType.STR : "db",
    IdentifierType.SYMBOL: "db",
    IdentifierType.CHAR: "db",
    IdentifierType.BOOLEAN: "db" 
}

def generate_label(label):
    return f"{label}:"

#if ident_name is "", will omit the label and just output for example dq 10, instead of x:\n\tdq 10. Think of it as an anonymous var
def generate_const(ident_obj,ident_name = ""):
    ident_type = ident_obj.typeof
    if ident_type == IdentifierType.INT or ident_type == IdentifierType.FLOAT:
        return f"{f'{ident_name}:\n\t' if len(ident_name) != 0 else "\t"}dq {ident_obj.value}"
    elif ident_type == IdentifierType.CHAR:
        return f"{f'{ident_name}:\n\t' if len(ident_name) != 0 else "\t"}db '{ident_obj.value[-1]}'"
    elif ident_type == IdentifierType.STR:
        return f"{f'{ident_name}:\n\t' if len(ident_name) != 0 else "\t"}db {ident_obj.value}, 0"
    elif ident_type == IdentifierType.SYMBOL:
        return f"{f'{ident_name}:\n\t' if len(ident_name) != 0 else "\t"}db '{ident_obj.value}', 0"
    elif ident_type == IdentifierType.BOOLEAN:
        return f"{f'{ident_name}:\n\t' if len(ident_name) != 0 else "\t"}db {'1' if ident_obj.value =='#t' else '0'}"

#offset is how many bytes from label the pair will be written at  
def generate_pair_body(label,pair_obj,offset = 0):
    emitted_elts = []
    #the pair_obj represents the empty list. both the car and cdr are set to 0x0
    # if pair_obj.car is None and pair_obj.cdr is None:
    if pair_obj.is_empty_list():
        return "\tdb 0x0\n\tdb 0x0\n"
    #the car of the pair_obj is the empty list
    if pair_obj.car is None:
        emitted_elts.append("db 0x0")
    elif pair_obj.car.typeof == IdentifierType.PAIR:
        emitted_elts.append(generate_pair_body(label,pair_obj.car.value,offset))
    elif pair_obj.car.typeof == IdentifierType.VECTOR:
        emitted_elts.append(generate_vector_body(label,pair_obj.car.value))
    else:
        #list elt is a constant
        emitted_elts.append(generate_const(pair_obj.car))
        
    #now handle the cdr
    if pair_obj.cdr is None:
        emitted_elts.append("\tdb 0x0")
    elif pair_obj.cdr.typeof == IdentifierType.PAIR:
        #dealing with a list. write asm for the ptr to cdr, and asm for the cdr itself
        next_pair_offset = pair_obj.car.get_size() + offset + 8
        emitted_elts.append(f"\tdq {label} + {str(next_pair_offset)}")
        emitted_elts.append(generate_pair_body(label,pair_obj.cdr.value,next_pair_offset))
    elif pair_obj.car.typeof == IdentifierType.VECTOR:
        emitted_elts.append(generate_vector_body(label,pair_obj.car.value))
    else:
        emitted_elts.append(generate_const(pair_obj.cdr))
    return '\n'.join(emitted_elts)

def generate_vector_body(label,vector_obj):
    emitted_elts = []
    offset = 0
    for ident_obj in vector_obj:
        if ident_obj.typeof == IdentifierType.PAIR:
            emitted_elts.append(generate_pair_body(label,ident_obj.value,offset))
        elif ident_obj.typeof == IdentifierType.VECTOR:
            emitted_elts.append(generate_vector_body(label,ident_obj.value))
        else:
            emitted_elts.append(generate_const(ident_obj))
            
        offset += ident_obj.get_size()
    return '\n'.join(emitted_elts) 