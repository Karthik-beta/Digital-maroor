PGDMP         ,                |            digital    15.3    15.4 	    K           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            L           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            M           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            N           1262    47233    digital    DATABASE     �   CREATE DATABASE digital WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_United States.1252';
    DROP DATABASE digital;
                postgres    false            �            1259    47396    location    TABLE     �   CREATE TABLE public.location (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(10) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);
    DROP TABLE public.location;
       public         heap    postgres    false            �            1259    47395    location_id_seq    SEQUENCE     �   ALTER TABLE public.location ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.location_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    241            H          0    47396    location 
   TABLE DATA           J   COPY public.location (id, name, code, created_at, updated_at) FROM stdin;
    public          postgres    false    241   	       O           0    0    location_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public.location_id_seq', 1, false);
          public          postgres    false    240            �           2606    47400    location location_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.location
    ADD CONSTRAINT location_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.location DROP CONSTRAINT location_pkey;
       public            postgres    false    241            H     x���?k�0��Y?�{�M�3֡�6�J�.rQ{m�~��c��p��C$�"c���t�Z�[��֤I!�T�T	�Z���R�"����y,w���w��-��J���{k���\�sO��o�4!�9U;��C�1�%T�QM�H�fkiwG\��J�%_�%[�v��z�b� H�����@��,N��Y~:@�a���:T~8@�w��� �c��~Ϧ_�pY~A��=�_���?$����e�K~M@9}�u���Ty���A}_�8�*�K?     